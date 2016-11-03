s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((\#\@~\^{w}+)|({w}+script\:|\@import[^a-zA-Z]|\;base64|base64,)|({w}+{s}*\([a-zA-Z ]+,[a-zA-Z ]+,[a-zA-Z ]+,[a-zA-Z ]+,[a-zA-Z ]+,[a-zA-Z ]+\))) printf('attack detected');
%%
