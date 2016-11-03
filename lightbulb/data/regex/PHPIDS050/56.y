s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((MERGE.*USING{s}*\()|(EXECUTE{s}*IMMEDIATE{s}*\")|({W}+{d}{s}+HAVING{s}+{d})|(MATCH{s}*[a-zA-Z\\(\\),+\-]+{s}*AGAINST{s}*\()) printf('attack detected');
%%
