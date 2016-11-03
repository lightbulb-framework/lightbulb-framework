s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((UNION{s}*(ALL)?{s}*[\(\[]{s}*SELECT)|(LIKE{s}*\"\%)|(\"{s}*LIKE{W}*[0-9\"])|(\"{s}*(AND|OR|XOR|NAND|NOT|\|\||\&\&){s}+[ a-zA-Z]+\={s}*[a-zA-Z]+{s}*HAVING)|((AND|OR|XOR|NAND|NOT|\|\||\&\&){s}[a-zA-Z\-]+{s}*[\=\&^].*[0-9\"])) printf('attack detected');
%%
