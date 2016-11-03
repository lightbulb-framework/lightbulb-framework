s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((union{s}*(all|distinct)?{s}*[\(\[]{s}*select)|({w}+{s}+like{s}+\")|(like{s}*\"\%)|(\"{s}*like{W}*[0-9\"])|(\"{s}*(n?and|x?or|not{s}|\|\||\&\&){s}+[ a-zA-Z]+\={s}*{w}+{s}*having)|(\"{s}*\*{s}*{w}+{W}+\")|(\"{s}*[^?a-zA-Z \=.,\;\/)(]+{s}*[(\@]*{s}*{w}+{W}+{w})|(select{s}*[\[\]\\(\\){s}{w}\.,\-]+from)) printf('attack detected');
%%
