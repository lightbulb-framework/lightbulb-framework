s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([^\: a-zA-Z,.\-\/?+]{s}*)?({s}*return{s}*)?(atob|btoa|charat|charcodeat|concat|crypto|frames|fromcharcode|indexof|lastindexof|match|replace|search|slice|split|substr|substring|escape)((1)[^a-zA-Z\"]|({s}*[^ a-zA-Z\",.+\-]))) printf('attack detected');
%%
