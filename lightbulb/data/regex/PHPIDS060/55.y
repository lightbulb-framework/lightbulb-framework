s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(({w}iif{s}*\()|(exec{s}+master\.)|(union{s}select{s}\@)|(union{s}*{w}*{s}*select)|(select.*{w}?user\()|(into[ +]+(dump|out)file{s}*\")) printf('attack detected');
%%
