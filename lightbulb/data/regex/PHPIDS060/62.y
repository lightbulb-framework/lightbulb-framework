s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((function[^(]*\([^)]*\))|((delete|void|throw|instanceof|new|typeof){W}+{w}+{s}*[\(\[])|([)\]]{s}*\.{s}*{w}+{s}*\=)|(\({s}*new{s}+{w}+{s}*\)\.)) printf('attack detected');
%%
