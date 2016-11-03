s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([^\: a-zA-Z,.\-\/?+]{s}*)?({s}*return{s}*)?(globalStorage|sessionStorage|callee|constructor|content|prototype|try|catch|top|call|apply|with|function|object|array|string|math|regex|boolean|location|settimeout|setinterval|void)((1)[^a-zA-Z\"]|({s}*[^ a-zA-Z\",.+\-]))) printf('attack detected');
%%
