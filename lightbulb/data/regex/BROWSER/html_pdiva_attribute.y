s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]

%%
\<(p|div|a){s}on(click|load)\=a\(\)\>\<\/(p|div|a)\> printf("attack\n");
%%