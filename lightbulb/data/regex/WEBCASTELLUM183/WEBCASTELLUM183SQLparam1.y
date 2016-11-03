s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((delete{s}+from)|(drop{s}+table)|(create{s}+(or{s}+replace{s}+)?(table|view|package|index|constraint))|(update{s}+.+{s}+set{s}+.+{s}*+\=)|(insert{s}+into{s}+.+({s}+|\))values|select{s}+.*(\*|,{s}*+{w}+{s}*+|dummy).*{s}+from|union.+select.+from|IF{s}*+\({s}*+USER{s}*+\({s}*+\){s}*+LIKE|root\@\%|BENCHMARK{s}*+\({s}*+[0123456789\*\+\-]+{s}*+,{s}*+SHA1{s}*+\([^\)]*+\)|exec.+[xs]p\_|into{s}+(out|dump)file|\;{s}*+GO{s}+EXEC|cmdshell{s}*+\(|\;{s}*+(drop|truncate|delete|insert|select|update|alter|create){s}+(table|view|index|package|constraint|user|trigger|or{s}+replace)|user\_name{s}*+\({s}*+\))|LIKE{s}+\'\%|AND{s}+(\({s}+)?ROWNUM{s}*+[\=\<\>]|AS{s}+.+{s}+FROM{s}+DUAL) printf('attack detected');
%%
