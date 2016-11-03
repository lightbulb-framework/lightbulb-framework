s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(((\@.+\={s}*\({s}*select)|({d}+{s}*(x?or|div|like|between|and){s}*{d}+{s}*[\-+])|(\/{w}+\;?{s}+(having|and|x?or|div|like|between|and|select){W})|({d}{s}+group{s}+by.+\()|((\;|\#|\-\-){s}*(drop|alter))|((\;|\#|\-\-){s}*(update|insert){s}*{w}{2})|([^a-zA-Z]SET{s}*\@{w}+)|((n?and|x?x?or|div|like|between|and|not|\|\||\&\&)[ (]+{w}+[ )]*[\!\=+]+[0-9 ]*[\"\'\`\=\\(\\)]))) printf('attack detected');
%%
