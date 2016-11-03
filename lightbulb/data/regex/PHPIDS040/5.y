s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((\;{W}*URL{s}*\=)|([^a-zA-Z \/]{s}*(location|referrer|name){s}*[^a-zA-Z \-])|(\{[^\:]+\:[^\}]+\})) printf('attack detected');
%%
