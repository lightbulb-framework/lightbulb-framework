s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((\%c0\%ae\/)|((\/|\\)+(home|conf|usr|etc|proc|opt|s?bin|local|dev|tmp|kern|[br]oot|sys|system|windows|winnt|program|\%[a\-z\_\-]{3}\%)(\/|\\))|((\/|\\)+inetpub|localstart\.asp|boot\.ini)) printf('attack detected');
%%
