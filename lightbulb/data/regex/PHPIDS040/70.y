s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((info\:\/)|({w}+\[\"\@{w}+)|((view\-source|about)\:{w}+)) printf('attack detected');
%%
