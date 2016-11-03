s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((\/\/{d}{4}\.{d}{4}\.{d}{4}.{d}{4})|(0x{w}{2}\.0x{w}{2}\.0x{w}{2}\.0x{w}{2})) printf('attack detected');
%%
