s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(((\/|\\)+(bin|home|conf|usr|etc|proc|opt|sbin|local|dev|tmp|kern|boot|root|sys|system|windows|winnt|program|\%[a\-z\_\-]{3}\%)(\/|\\))|((\/|\\)+inetpub|localstart\.asp|boot\.ini)) printf('attack detected');
%%
