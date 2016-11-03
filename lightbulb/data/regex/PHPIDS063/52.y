s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((alter{s}*{w}+.*character{s}+set{s}+{w}+)|(\"\;{s}*waitfor{s}+time{s}+\")|(\"\;.*\:{s}*goto)) printf('attack detected');
%%
