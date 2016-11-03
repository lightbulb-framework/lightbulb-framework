s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(({w}+]?\=(http|ftp|https)\:\/\/)) printf('attack detected');
%%
