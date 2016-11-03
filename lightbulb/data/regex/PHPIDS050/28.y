s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((firefoxurl\:{w}+\|)|((file|res|telnet|nntp|news|mailto|chrome){s}*\:{s}*[\%\&\#xu\/]+)|(wyciwyg|firefoxurl{s}*\:{s}*\/{s}*\/)) printf('attack detected');
%%
