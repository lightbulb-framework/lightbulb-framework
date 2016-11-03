s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((\={s}*(top|this|window|content|self|frames|\_content))|(\/{s}*[gimx]*{s}*[)\}])|([^ ]{s}*\={s}*script)|(\.{s}*constructor)|(default{s}+xml{s}+namespace{s}*\=)|(\/{s}*\+[^+]+{s}*\+{s}*\/)) printf('attack detected');
%%
