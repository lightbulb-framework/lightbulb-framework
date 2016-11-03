s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((function[^(]*\([^)]*\))|(new{s}*{w}+{s}*[\(\[])|([)\]]{s}*\.{s}*{w}+{s}*\=)) printf('attack detected');
%%
