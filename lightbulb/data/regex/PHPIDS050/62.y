s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((function[^(]*\([^)]*\))|((delete|void|throw|.*in{s}+|instanceof|new|typeof){s}*{w}+{s}*[\(\[])|([)\]]{s}*\.{s}*{w}+{s}*\=)) printf('attack detected');
%%
