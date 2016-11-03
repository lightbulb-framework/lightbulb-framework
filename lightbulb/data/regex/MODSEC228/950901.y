s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((([ \'\"\`\(\)]*)([0-9a-zA-Z]++)([ \'\"\`\(\)]*)((\=|\<\=\>|r?like|sounds{s}+like|regexp)([ \'\"\`\(\)]*)\2|(\!\=|\<\=|\>\=|\<\>|\<|\>|\^|is{s}+not|not{s}+like|not{s}+regexp)([ \'\"\`\(\)]*)([0-9a-zA-Z]+)))) printf('attack detected');
%%
