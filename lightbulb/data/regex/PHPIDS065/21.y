s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((,{s}*(alert|showmodaldialog|eval){s}*,)|(\:{s}*eval{s}*[^ ])|([^\: a-zA-Z,.\/?+\-]{s}*)?({s}*return{s}*)?((document{s}*\.)?(.+\/)?(alert|eval|msgbox|showmodaldialog|prompt|write(ln)?|confirm|dialog|open)){s}*([^a\-z \-]|({s}*[^ a-zA-Z,.\@\/+\-]))|(java[ \/]*\.[ \/]*lang)|({w}{s}*\={s}*new{s}+{w}+)|(\&{s}*{w}+{s}*\)[^,])|(\+[0-9\!\@\#\$\%\^\&\*\(\)\-\_\+\=\{\}\[\]\;\:\|\?\/\.\>\,\<\`\~]*new{s}+{w}+[0-9\!\@\#\$\%\^\&\*\(\)\-\_\+\=\{\}\[\]\;\:\|\?\/\.\>\,\<\`\~]*\+)|(document\.{w})) printf('attack detected');
%%
