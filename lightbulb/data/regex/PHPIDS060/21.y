s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((,{s}*(alert|showmodaldialog|eval){s}*,)|(\:{s}*eval{s}*[^ ])|([^\: a-zA-Z,.\/?+\-]{s}*)?t)|(\<scri)|(\<{w}+\:{w}+)) printf('attack detected');
%%
