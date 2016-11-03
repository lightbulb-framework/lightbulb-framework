s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([^*\: a-zA-Z,.\/?+\-]{s}*)?({s}*return{s}*)?(create(element|attribute|textnode)|[a\-z]+Events?|getelement{w}+|appendchild|createrange|createcontextualfragment|removenode|parentnode|decodeuricomponent|{w}ettimeout|useragent)((1)[^a-zA-Z\%\"]|({s}*[^\@ a-zA-Z\%\",.+\-]))) printf('attack detected');
%%
