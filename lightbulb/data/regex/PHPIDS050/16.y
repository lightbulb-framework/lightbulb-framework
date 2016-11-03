s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([^\: a-zA-Z,.\-\/?+]{s}*)?({s}*return{s}*)?(alert|isnan|isnull|msgbox|expression|prompt|write(ln)?|confirm|dialog|urn|(un)?eval|exec|execscript|toString|Execute|window|unescape|navigate)((1)[^a-zA-Z\%\"]|({s}*[^ a-zA-Z\%\",.+\-]))) printf('attack detected');
%%
