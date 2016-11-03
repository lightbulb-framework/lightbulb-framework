s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((ALTER{s}*{w}+.*CHARACTER{s}+SET{s}+{w}+)|(\"\;{s}*WAITFOR{s}+TIME{s}+\")|(\"\;.*\:{s}*GOTO)) printf('attack detected');
%%
