s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([^\: a-zA-Z,.\-\/?+]{s}*)?({s}*return{s}*)?(hash|name|href|source|pathname|close|port|protocol|search|replace|back|forward|go|document|window|self|this|parent|cookie|innerhtml|innertext|outerhtml)((1)[^a-zA-Z\"]|({s}*[^ a-zA-Z\",.+\-]))) printf('attack detected');
%%
