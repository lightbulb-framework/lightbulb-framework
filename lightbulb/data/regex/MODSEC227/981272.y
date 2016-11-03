s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(((sleep\(({s}*)({d}*)({s}*)\)|benchmark\((.*)\,(.*)\)))) printf('attack detected');
%%
