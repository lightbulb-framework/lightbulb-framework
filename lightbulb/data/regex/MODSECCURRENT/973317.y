s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((\<OBJECT[ \/+\t].*((type)|(codetype)|(classid)|(code)|(data))[ \/+\t]*\=)) printf('attack detected');
%%
