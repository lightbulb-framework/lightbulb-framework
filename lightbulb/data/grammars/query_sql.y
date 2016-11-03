S: A main
main: query_exp
query_exp: groupby_exp | order_exp | limit_exp | procedure_exp | into_exp | for_exp | lock_exp | ; select_exp | union_exp | join_exp
groupby_exp: GROUP BY column_ref ascdesc_exp
order_exp: ORDER BY column_ref ascdesc_exp
limit_exp: LIMIT intnum
into_exp: INTO output_exp intnum
procedure_exp: PROCEDURE name ( literal )
literal: string | intnum
select_exp: SELECT name
union_exp: UNION select_exp
ascdesc_exp: ASC | DESC
column_ref: name
join_exp: JOIN name ON name
for_exp: FOR UPDATE
lock_exp: LOCK IN SHARE MODE
output_exp: OUTFILE | DUMPFILE
string: name
intnum: 1
name: A
