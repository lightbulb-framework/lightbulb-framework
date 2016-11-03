s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(.+application\/x\-shockwave\-flash|image\/svg\+xml|text\/(css|html|ecmascript|javascript|vbscript|x\-(javascript|scriptlet|vbscript)).+) printf('attack detected');
%%
