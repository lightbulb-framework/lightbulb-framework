s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(((do|for|while){s}*\([^\;]+\;+\))|((^|{W})on{w}+{s}*\=[a-zA-Z\!\@\#\$\%\^\&\*\(\)\-\_\+\=\{\}\[\]\;\:\|\?\/\.\>\,\<\`\~]*(on{w}+|alert|eval|print|confirm|prompt))|(groups\={d}+\({w}+\))|((.)\1{128,})) printf('attack detected');
%%
