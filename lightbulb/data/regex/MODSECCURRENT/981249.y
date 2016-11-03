s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((([\"\'\`]{s}+and{s}*\={W})|(\({s}*select{s}*{w}+{s}*\()|(\*\/from)|(\+{s}*{d}+{s}*\+{s}*\@)|({w}[\"\'\`]{s}*([\-+\=|\@]+{s}*)+[0-9(])|(coalesce{s}*\(|\@\@{w}+{s}*[^a-zA-Z ])|({W}\!+[\"\'\`]{w})|([\"\'\`]\;{s}*(if|while|begin))|([\"\'\`][0-9 ]+\={s}*{d})|(order{s}+by{s}+if{w}*{s}*\()|([ (]+case{d}*{W}.+[tw]hen[ (]))) printf('attack detected');
%%
