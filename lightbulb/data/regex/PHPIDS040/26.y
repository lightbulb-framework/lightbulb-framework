s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(((\$\$?{s}*{w}?|ext[ .]+{w}+|cssquery|dojo[ .]+{w}+){s}*\(|\_\_gwt\_)) printf('attack detected');
%%
