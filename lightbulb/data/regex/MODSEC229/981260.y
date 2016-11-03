s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(((\A|[0-9^])0x[0-9a\-f]{3}[0-9a\-f]*)+) printf('attack detected');
%%
