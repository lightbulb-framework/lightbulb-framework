s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((binding{s}?\=|moz\-binding|behavior{s}?\=)|([ \/]style{s}*\={s}*[\-\\])) printf('attack detected');
%%
