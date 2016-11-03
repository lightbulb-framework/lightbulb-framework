s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
(((m(s(ysaccessobjects|ysaces|ysobjects|ysqueries|ysrelationships|ysaccessstorage|ysaccessxml|ysmodules|ysmodules2|db)|aster\.\.sysdatabases|ysql\.db)|s(ys(\.database\_name|aux)|chema({W}*\(|\_name)|qlite(\_temp)?\_master)|d(atabas|b\_nam)e{W}*\(|information\_schema|pg\_(catalog|toast)|northwind|tempdb))) printf('attack detected');
%%
