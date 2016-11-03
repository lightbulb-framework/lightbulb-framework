s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((\<EMBED[ \/+\t].*((src)|(type)).*\=)) printf('attack detected');
%%
