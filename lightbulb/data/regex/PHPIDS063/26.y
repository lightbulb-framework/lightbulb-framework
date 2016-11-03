s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([^\: a-zA-Z]+{s}*[^a-zA-Z\/](href|protocol|host|hostname|pathname|hash|port|cookie)[^a-zA-Z])) printf('attack detected');
%%
