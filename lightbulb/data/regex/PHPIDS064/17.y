s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([^*\: a-zA-Z,.\/?+\-]{s}*)?({s}*return{s}*)?(hash|name|href|navigateandfind|source|pathname|close|constructor|port|protocol|assign|replace|back|forward|document|ownerdocument|window|self|parent|frames|\_?content|date|cookie|innerhtml|innertext|csstext+?|outerhtml|print|moveby|resizeto|createstylesheet|stylesheets)((1)[^a-zA-Z\%\"]|({s}*[^\@\/ a-zA-Z\%,.+\-]))) printf('attack detected');
%%
