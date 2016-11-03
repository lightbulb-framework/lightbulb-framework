s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([^\: a-zA-Z]+{s}*[^a-zA-Z\/](href|protocol|host{w}*|pathname|search|hash|port|cookie)[^a-zA-Z])) printf('attack detected');
%%
