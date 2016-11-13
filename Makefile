init:
	export LC_ALL=en_US.UTF-8
	export LANG=en_US.UTF-8
	sudo python setup.py install
	sudo pip install -r requirements.txt
test:
	nosetests tests
