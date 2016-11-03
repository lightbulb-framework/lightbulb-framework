s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((SELECT{s}*pg\_sleep)|(WAITFOR{s}*DELAY{s}?\"+{s}?{d})|(\;{s}*SHUTDOWN{s}*(\-\-|\#|\/\*|\{))) printf('attack detected');
%%
