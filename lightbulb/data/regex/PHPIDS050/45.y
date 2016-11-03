s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((UNION{s}*(ALL)?{s}*[\(\[]{s}*SELECT)|(LIKE{s}*\"\%)|(\"{s}*LIKE{W}*[0-9\"])|(\"{s}*(AND|OR|XOR|NAND|NOT|\|\||\&\&){s}+[ a-zA-Z]+\={s}*{w}+{s}*HAVING)|(\"{s}*\*{s}*{w}+{W}+\")|(\"{s}*[^a-zA-Z \=.,\/)]+{s}*[(\@]*{s}*{w}+{W}+{w})) printf('attack detected');
%%
