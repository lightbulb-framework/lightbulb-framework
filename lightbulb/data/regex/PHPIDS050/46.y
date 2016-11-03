s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(((AND|OR|XOR|NAND|NOT|\|\||\&\&){s}+[ a-zA-Z+]+(REGEXP{s}*\(|SOUNDS{s}+LIKE{s}*\"|[0-9\=]+x))|(\"{s}*{d}{s}*(\-\-|\#))|(\"[\%\&\<\>^\=]+{d}{s}*(\=|OR))|(\"{W}+[a-zA-Z+\-]+{s}*\={s}*{d}{W}+\")|(\"{s}*is{s}*{d}.+\"?{w})|(\"\|?[a-zA-Z\-]{3}[^a-zA-Z .]+\")|(\"{s}*is{s}*[0-9.]+{s}*{W}.*\")) printf('attack detected');
%%
