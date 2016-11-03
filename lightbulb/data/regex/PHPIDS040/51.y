s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(((\;|\#|\-\-){s}*(DROP|ALTER))|((\;|\#|\-\-){s}*(UPDATE|INSERT){s}*{w}{2})|([^a-zA-Z]SET{s}*\@{w}+)|((AND|OR|XOR|NAND|NOT|\|\||\&\&)[ a-zA-Z]+[\!\=+]+[0-9 ]*[\"\=(])) printf('attack detected');
%%
