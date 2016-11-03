s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((from{s}+information\_schema{W})|(((current\_)?user|database|schema|connection\_id){s}*\([^\)]*)|(\"\;?{s}*(select|union|having){s}*[0-9\"(])|({w}iif{s}*\()|(exec{s}+master\.)|(union{s}select{s}\@)|(union[a-zA-Z( ]*select)|(select.*{w}?user\()|(into[ +]+(dump|out)file{s}*\")) printf('attack detected');
%%
