s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((\){s}*\[)|([^*\"\: a-zA-Z,.\/?+\-]{s}*)?({s}*return{s}*)?(globalstorage|sessionstorage|postmessage|callee|constructor|content|domain|prototype|try|catch|top|call|apply|url|function|object|array|string|math|if|for{s}*(each)?|elseif|case|switch|regex|boolean|location|(ms)?setimmediate|settimeout|setinterval|void|setexpression|namespace|while)((1)[^a-zA-Z\%\"]|({s}*[^\@ a-zA-Z\%\".+\-\/]))) printf('attack detected');
%%
