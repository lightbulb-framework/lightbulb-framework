s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([^*\: a-zA-Z,.\/?+\-]{s}*)?({s}*return{s}*)?(atob|btoa|charat|charcodeat|charset|concat|crypto|frames|fromcharcode|indexof|lastindexof|match|navigator|toolbar|menubar|replace|regexp|slice|split|substr|substring|escape|{w}+codeuri{w}*)((1)[^a-zA-Z\%\"]|({s}*[^\@ a-zA-Z\%\",.+\-]))) printf('attack detected');
%%
