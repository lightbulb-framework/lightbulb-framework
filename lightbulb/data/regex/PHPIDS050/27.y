s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((data\:(.)*,)|({w}+{s}*\={W}*{w}+\:)|(jar\:{w}+\:)) printf('attack detected');
%%
