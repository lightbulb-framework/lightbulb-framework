s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(((ping(.*)[\-(.*)a-zA-Z|a-zA-Z(.*)\-]))) printf('attack detected');
%%
