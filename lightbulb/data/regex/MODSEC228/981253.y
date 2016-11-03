s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(((procedure{s}+analyse{s}*\()|(\;{s}*(declare|open){s}+[a-zA-Z\-]+)|(create{s}+(procedure|function){s}*{w}+{s}*\({s}*\){s}*\-)|(declare[^a-zA-Z]+[\@\#]{s}*{w}+)|(exec{s}*\({s}*\@))) printf('attack detected');
%%
