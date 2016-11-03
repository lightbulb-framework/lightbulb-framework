s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((CREATE{s}+function{s}+{w}+{s}+returns)|(\;{s}*(SELECT|CREATE|RENAME|TRUNCATE|LOAD|ALTER|DELETE|UPDATE|INSERT|DESC){s}*{w}{2})) printf('attack detected');
%%
