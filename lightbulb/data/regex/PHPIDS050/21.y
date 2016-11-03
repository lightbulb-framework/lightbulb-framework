s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((,{s}*(alert|eval){s}*,)|(\:{s}*eval{s}*[^ ])|([^\: a-zA-Z,.\-\/?+]{s}*)?({s}*return{s}*)?((document{s}*\.)?(.+\/)?(alert|eval|msgbox|prompt|write(ln)?|confirm|dialog|open))((1)[^a-zA-Z]|({s}*[^ a-zA-Z,.+\-]))|(java[ \/]*\.[ \/]*lang)|({w}{s}*\={s}*new{s}+{w}+)) printf('attack detected');
%%
