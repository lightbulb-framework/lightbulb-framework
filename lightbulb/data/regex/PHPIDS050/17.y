s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([^\: a-zA-Z,.\-\/?+]{s}*)?({s}*return{s}*)?(hash|name|href|source|pathname|close|constructor|port|protocol|replace|back|forward|go|document|window|self|parent|frames|\_?content|date|cookie|innerhtml|innertext|outerhtml|print|moveby|resizeto)((1)[^a-zA-Z\%\"]|({s}*[^ a-zA-Z\%\",.+\-]))) printf('attack detected');
%%
