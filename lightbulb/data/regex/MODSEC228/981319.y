s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(((\!\=|\&\&|\|\||\>\>|\<\<|\>\=|\<\=|\<\>|\<\=\>|xor|rlike|regexp|isnull)|(not{s}+between{s}+0{s}+and)|(is{s}+null)|(like{s}+null)|((^|{W})in[+ ]*\([0-9 \"]+[^\\(\\)]*\))|(xor|\<\>|rlike({s}+binary)?)|(regexp{s}+binary))) printf('attack detected');
%%
