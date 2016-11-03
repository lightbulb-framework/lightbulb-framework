s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([^* a-zA-Z,.\/?+\-]{s}*)?({s}*return{s}*)?(alert|inputbox|showmodaldialog|infinity|isnan|isnull|iterator|msgbox|expression|prompt|write(ln)?|confirm|dialog|urn|(un)?eval|exec|execscript|tostring|status|execute|window|unescape|navigate|jquery|getscript|extend|prototype)((1)[^a-zA-Z\%\"]|({s}*[^\@ a-zA-Z\%\",.\:\/+\-]))) printf('attack detected');
%%
