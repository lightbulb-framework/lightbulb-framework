s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((({s}exec{s}+xp\_cmdshell)|([\"\'\`]{s}*\!{s}*[\"\'\`a-zA-Z])|(from{W}+information\_schema{W})|(((current\_)?user|database|schema|connection\_id){s}*\([^\)]*)|([\"\'\`]\;?{s}*(select|union|having){s}*[^ ])|({w}iif{s}*\()|(exec{s}+master\.)|(union{s}select{s}\@)|(union[a-zA-Z( ]*select)|(select.*{w}?user\()|(into[ +]+(dump|out)file{s}*[\"\'\`]))) printf('attack detected');
%%
