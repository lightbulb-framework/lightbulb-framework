s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((\*\/FROM)|({w}\"{s}*([\-+\=|\@]+{s}*)+[0-9(])|(COALESCE{s}*\(|\@\@{w}+{s}*[^a-zA-Z ])|({W}\!+\"{w})|(\"\;{s}*(if|while|begin))|(\"[0-9 ]+\={s}*{d})) printf('attack detected');
%%
