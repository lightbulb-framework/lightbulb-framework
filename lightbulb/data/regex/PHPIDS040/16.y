s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([^\: a-zA-Z,.\-\/?+]{s}*)?({s}*return{s}*)?(create(Element|Attribute|TextNode)|{w}+Events?|getElement{w}+|appendChild|createRange|createContextualFragment|removeNode|parentNode|decodeURIComponent|{w}etTimeout|userAgent)((1)[^a-zA-Z\"]|({s}*[^ a-zA-Z\",.+\-]))) printf('attack detected');
%%
