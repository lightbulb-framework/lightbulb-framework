s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((([\;]+|(\<{s}\?\%](php)?)).*[^a-zA-Z](echo|print|print\_r|var\_dump|[fp]open))|(\;{s}*rm{s}+\-{w}+{s}+)|(\;.*\{.*\${w}+{s}*\=)|(\${w}+{s}*\[\]{s}*\={s}*)) printf('attack detected');
%%
