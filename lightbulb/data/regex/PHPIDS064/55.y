s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((\"{s}*\!{s}*[\"a-zA-Z])|(from{s}+information\_schema{W})|(((current\_)?user|database|schema|connection\_id){s}*\([^\)]*)|(\"\;?{s}*(select|union|having){s}*[^ )|(a-zA-Ziif *\()|(exec +master\.)|(union select \@)|(union[a-zA-Z( ]*select)|(select.*{w}?user\()|(into[ +]+(dump|out)file{s}*\")) printf('attack detected');
%%
