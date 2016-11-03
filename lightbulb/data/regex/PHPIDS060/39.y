s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((\\x[01FE]{w})|(\%[01FE]{w})|(\&\#[01FE]{w})|(\\[01FE][0\-9a\-f])|(\&\#x[01FE]{w})) printf('attack detected');
%%
