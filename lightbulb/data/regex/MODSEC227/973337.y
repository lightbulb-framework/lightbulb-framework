s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((i)([ \"\'\`\;\/0\-9\=]+on{w}+{s}*\=)) printf('attack detected');
%%
