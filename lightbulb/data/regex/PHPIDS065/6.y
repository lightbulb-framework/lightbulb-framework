s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((with{s}*\({s}*.+{s}*\){s}*{w}+{s}*\()|((do|while|for){s}*\([^)]*\){s}*\{)|(\/[a-zA-Z ]*\[{W}*{w})) printf('attack detected');
%%
