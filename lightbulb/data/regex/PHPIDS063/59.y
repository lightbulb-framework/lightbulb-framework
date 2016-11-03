s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((([\;]+|(\<{s}\?\%](php)?)).*(define|eval|file\_get\_contents|include|require|require\_once|set|shell\_exec|phpinfo|system|passthru|preg\_{w}+|execute){s}*[\"(\@])) printf('attack detected');
%%
