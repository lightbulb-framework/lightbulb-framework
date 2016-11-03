s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([^\: a-zA-Z,.\-\/?+]{s}*)?({s}*return{s}*)?(atob|btoa|charat|charcodeat|charset|concat|crypto|frames|fromcharcode|indexof|lastindexof|match|navigator|replace|regexp|slice|split|status|substr|substring|escape|{w}+codeURI{w}*)((1)[^a-zA-Z\%\"]|({s}*[^ a-zA-Z\%\",.+\-]))) printf('attack detected');
%%
