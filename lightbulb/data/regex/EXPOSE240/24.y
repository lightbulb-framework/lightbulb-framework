s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(([\".]script{s}*\()|(\$\$?{s}*\({s}*[a-zA-Z\"])|(\/[a-zA-Z ]+\/\.)|(\={s}*\/{w}+\/{s}*\.)|((this|window|top|parent|frames|self|content)\[{s}*[(,\"]*{s}*[a-zA-Z\$])|(,{s}*new{s}+{w}+{s}*[,\;)])) printf('attack detected');
%%
