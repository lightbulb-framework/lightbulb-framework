s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]

%%
(\<(p|div|form|input){s}onclick\=a\(\)\>\<\/(p|div|form|input)\>)  printf("attack\n");
%%