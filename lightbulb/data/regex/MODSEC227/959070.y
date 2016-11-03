s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((having){s}+({d}{1,10}|\'[^\=]{1,10}\'){s}*[\=\<\>]|(execute({s}{1,5}[a-zA-Z\.$]{1,5}{s}{0,3})?\()|having{s}?({d}{1,10}|[\'\"][^\=]{1,10}[\'\"]){s}?[\=\<\>]+|(create{s}+?table.{0,20}?\()|(like{W}*char{W}*\()|(((select(.*)case|from(.*)limit|order{s}by)))|exists{s}({s}select|select\Sif(null)?{s}\(|select\Stop|select\Sconcat|system{s}\(|(having){s}+({d}{1,10})|\'[^\=]{1,10}\')) printf('attack detected');
%%
