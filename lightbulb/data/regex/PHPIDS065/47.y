s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([0-9\!\@\#\$\%\^\&\*\(\)\-\_\+\=\{\}\[\]\;\:\|\?\/\.\>\,\<\`\~]{s}+as{s}*[\"a-zA-Z]+{s}*from)|(^[0-9\!\@\#\$\%\^\&\*\(\)\-\_\+\=\{\}\[\]\;\:\|\?\/\.\>\,\<\`\~]+{s}*(union|select|create|rename|truncate|load|alter|delete|update|insert|desc))|((select|create|rename|truncate|load|alter|delete|update|insert|desc){s}+(concat|char|load\_file){s}?\()|(end{s}*\)\;)|(\"{s}+regexp{W})|([ (]load\_file{s}*\()) printf('attack detected');
%%
