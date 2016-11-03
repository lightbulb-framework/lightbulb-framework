s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((CREATE{s}+(PROCEDURE|FUNCTION){s}*{w}+{s}*\({s}*\){s}*\-)|(declare[^a-zA-Z]+[\@\#]{s}*{w}+)|(exec{s}*\({s}*\@)) printf('attack detected');
%%
