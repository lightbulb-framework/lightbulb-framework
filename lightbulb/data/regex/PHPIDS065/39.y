s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((\\x[01fe][0-9b\-ce\-f])|(\%[01fe][0-9b\-ce\-f])|(\&\#[01fe][0-9b\-ce\-f])|(\\[01fe][0-9b\-ce\-f])|(\&\#x[01fe][0-9b\-ce\-f])) printf('attack detected');
%%
