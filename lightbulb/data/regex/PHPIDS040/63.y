s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((([\;]+|(\<{s}\?\%](php)?)).*(echo|print|print\_r|var\_dump|fopen|popen))|(\;{s}*rm{s}+\-{w}+{s}+)|(\;.*\{.*\${w}+{s}*\=)) printf('attack detected');
%%
