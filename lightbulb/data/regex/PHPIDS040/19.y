s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([^\: a-zA-Z,.\-\/?+]{s}*)?({s}*return{s}*)?(join|pop|push|reverse|shift|slice|splice|sort|unshift)((1)[^a-zA-Z\"]|({s}*[^ a-zA-Z\",.+\-]))) printf('attack detected');
%%
