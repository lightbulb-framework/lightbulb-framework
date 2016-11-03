s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(({W}IIF{s}*\()|(EXEC{s}+master\.)|(UNION{s}SELECT{s}\@)|(UNION{s}*{w}*{s}*SELECT)|(SELECT.*{w}?user\()|(INTO[ +]+(DUMP|OUT)FILE{s}*\")) printf('attack detected');
%%
