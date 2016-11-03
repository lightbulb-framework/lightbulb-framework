s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(((create{s}+function{s}+{w}+{s}+returns)|(\;{s}*(select|create|rename|truncate|load|alter|delete|update|insert|desc){s}*[\[(]?{w}{2}))) printf('attack detected');
%%
