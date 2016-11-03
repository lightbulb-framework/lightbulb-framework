s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(({w}+]?\=(https?|ftp)\:)|(\{{s}*\${s}*\{)) printf('attack detected');
%%
