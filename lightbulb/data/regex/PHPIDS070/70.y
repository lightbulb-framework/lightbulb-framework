s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((\[\$(ne|eq|lte?|gte?|n?in|mod|all|size|exists|type|slice|or)\])) printf('attack detected');
%%
