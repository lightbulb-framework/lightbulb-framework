s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((groups\={d}+\({w}+\))|({w}{256,}|{W}{256,}|{s}{256,}|\/.+{s}http\/{d}.{d}{s}?\\+{w}\\+{w}|(\:..){4}|{W}{d}+\/{d}{20,})) printf('attack detected');
%%
