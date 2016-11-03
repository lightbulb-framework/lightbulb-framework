s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(((select{s}*pg\_sleep)|(waitfor{s}*delay{s}?[\"\'\`]+{s}?{d})|(\;{s}*shutdown{s}*(\;|\-\-|\#|\/\*|\{)))) printf('attack detected');
%%
