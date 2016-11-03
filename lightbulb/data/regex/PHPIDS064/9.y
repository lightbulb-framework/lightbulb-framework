s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((\\u00[a\-f0\-9]{2})|(\\x0*[a\-f0\-9]{2})|(\\{d}{2,3})) printf('attack detected');
%%
