#!/bin/bash
set -e

DB_NAME=${DB_NAME:-}
DB_USER=${DB_USER:-}
DB_PASS=${DB_PASS:-}

DB_REMOTE_ROOT_NAME=${DB_REMOTE_ROOT_NAME:-}
DB_REMOTE_ROOT_PASS=${DB_REMOTE_ROOT_PASS:-}
DB_REMOTE_ROOT_HOST=${DB_REMOTE_ROOT_HOST:-"172.17.0.1"}

MYSQL_CHARSET=${MYSQL_CHARSET:-"utf8"}
MYSQL_COLLATION=${MYSQL_COLLATION:-"utf8_unicode_ci"}

create_data_dir() {
  mkdir -p ${MYSQL_DATA_DIR}
  chmod -R 0700 ${MYSQL_DATA_DIR}
  chown -R ${MYSQL_USER}:${MYSQL_USER} ${MYSQL_DATA_DIR}
}

create_run_dir() {
  mkdir -p ${MYSQL_RUN_DIR}
  chmod -R 0755 ${MYSQL_RUN_DIR}
  chown -R ${MYSQL_USER}:root ${MYSQL_RUN_DIR}
}

create_log_dir() {
  mkdir -p ${MYSQL_LOG_DIR}
  chmod -R 0755 ${MYSQL_LOG_DIR}
  chown -R ${MYSQL_USER}:${MYSQL_USER} ${MYSQL_LOG_DIR}
}

listen() {
  sed -e "s/^bind-address\(.*\)=.*/bind-address = $1/" -i /etc/mysql/my.cnf
}

apply_configuration_fixes() {
  # disable error log
  sed 's/^log_error/# log_error/' -i /etc/mysql/my.cnf

  # Fixing StartUp Porblems with some DNS Situations and Speeds up the stuff
  # http://www.percona.com/blog/2008/05/31/dns-achilles-heel-mysql-installation/
  cat > /etc/mysql/conf.d/mysql-skip-name-resolv.cnf <<EOF
[mysqld]
skip_name_resolve
EOF
}

remove_debian_systen_maint_password() {
  #
  # the default password for the debian-sys-maint user is randomly generated
  # during the installation of the mysql-server package.
  #
  # Due to the nature of docker we blank out the password such that the maintenance
  # user can login without a password.
  #
  sed 's/password = .*/password = /g' -i /etc/mysql/debian.cnf
}

initialize_mysql_database() {
  # initialize MySQL data directory
  if [ ! -d ${MYSQL_DATA_DIR}/mysql ]; then
    echo "Installing database..."
    mysql_install_db --user=mysql >/dev/null 2>&1

    # start mysql server
    echo "Starting MySQL server..."
    /usr/bin/mysqld_safe >/dev/null 2>&1 &

    # wait for mysql server to start (max 30 seconds)
    timeout=30
    echo -n "Waiting for database server to accept connections"
    while ! /usr/bin/mysqladmin -u root status >/dev/null 2>&1
    do
      timeout=$(($timeout - 1))
      if [ $timeout -eq 0 ]; then
        echo -e "\nCould not connect to database server. Aborting..."
        exit 1
      fi
      echo -n "."
      sleep 1
    done
    echo

    ## create a localhost only, debian-sys-maint user
    ## the debian-sys-maint is used while creating users and database
    ## as well as to shut down or starting up the mysql server via mysqladmin
    echo "Creating debian-sys-maint user..."
    mysql -uroot -e "GRANT ALL PRIVILEGES on *.* TO 'debian-sys-maint'@'localhost' IDENTIFIED BY '' WITH GRANT OPTION;"

    if [ -n "${DB_REMOTE_ROOT_NAME}" -a -n "${DB_REMOTE_ROOT_HOST}" ]; then
      echo "Creating remote user \"${DB_REMOTE_ROOT_NAME}\" with root privileges..."
      mysql -uroot \
      -e "GRANT ALL PRIVILEGES ON *.* TO '${DB_REMOTE_ROOT_NAME}'@'${DB_REMOTE_ROOT_HOST}' IDENTIFIED BY '${DB_REMOTE_ROOT_PASS}' WITH GRANT OPTION; FLUSH PRIVILEGES;"
    fi

    /usr/bin/mysqladmin --defaults-file=/etc/mysql/debian.cnf shutdown
  fi
}

create_users_and_databases() {
  # create new user / database
  if [ -n "${DB_USER}" -o -n "${DB_NAME}" ]; then
    /usr/bin/mysqld_safe >/dev/null 2>&1 &

    # wait for mysql server to start (max 30 seconds)
    timeout=30
    while ! /usr/bin/mysqladmin -u root status >/dev/null 2>&1
    do
      timeout=$(($timeout - 1))
      if [ $timeout -eq 0 ]; then
        echo "Could not connect to mysql server. Aborting..."
        exit 1
      fi
      sleep 1
    done

    if [ -n "${DB_NAME}" ]; then
      for db in $(awk -F',' '{for (i = 1 ; i <= NF ; i++) print $i}' <<< "${DB_NAME}"); do
        echo "Creating database \"$db\"..."
        mysql --defaults-file=/etc/mysql/debian.cnf \
          -e "CREATE DATABASE IF NOT EXISTS \`$db\` DEFAULT CHARACTER SET \`$MYSQL_CHARSET\` COLLATE \`$MYSQL_COLLATION\`;"
          if [ -n "${DB_USER}" ]; then
            echo "Granting access to database \"$db\" for user \"${DB_USER}\"..."
            mysql --defaults-file=/etc/mysql/debian.cnf \
            -e "GRANT ALL PRIVILEGES ON \`$db\`.* TO '${DB_USER}' IDENTIFIED BY '${DB_PASS}';"
          fi
        done
    fi
    /usr/bin/mysqladmin --defaults-file=/etc/mysql/debian.cnf shutdown
  fi
}

create_data_dir
create_run_dir
create_log_dir

# allow arguments to be passed to mysqld_safe
if [[ ${1:0:1} = '-' ]]; then
  EXTRA_ARGS="$@"
  set --
elif [[ ${1} == mysqld_safe || ${1} == $(which mysqld_safe) ]]; then
  EXTRA_ARGS="${@:2}"
  set --
fi

# default behaviour is to launch mysqld_safe
if [[ -z ${1} ]]; then
  listen "127.0.0.1"
  apply_configuration_fixes
  remove_debian_systen_maint_password
  initialize_mysql_database
  create_users_and_databases
  listen "0.0.0.0"
  exec $(which mysqld_safe) $EXTRA_ARGS
else
  exec "$@"
fi
