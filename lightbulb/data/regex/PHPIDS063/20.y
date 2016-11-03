s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([^*\: a-zA-Z,.\/?+\-]{s}*)?({s}*return{s}*)?(globalstorage|sessionstorage|postmessage|callee|constructor|content|domain|prototype|try|catch|top|call|apply|url|function|object|array|string|math|if|elseif|case|switch|regex|boolean|location|settimeout|setinterval|void|setexpression|namespace|while)((1)[^a-zA-Z\%\"]|({s}*[^\@ a-zA-Z\%\",.+\-]))) printf('attack detected');
%%
