S: A main
main: search_condition 
search_condition: OR predicate | AND predicate 
predicate: comparison_predicate | between_predicate | like_predicate | test_for_null | in_predicate | all_or_any_predicate | existence_test
comparison_predicate: scalar_exp comparison scalar_exp | scalar_exp COMPARISON subquery
between_predicate: scalar_exp BETWEEN scalar_exp AND scalar_exp
like_predicate: scalar_exp LIKE atom 
test_for_null: column_ref IS NULL
in_predicate: scalar_exp IN ( subquery ) | scalar_exp IN ( atom ) 
all_or_any_predicate: scalar_exp comparison any_all_some subquery
existence_test: EXISTS subquery
scalar_exp:  scalar_exp op scalar_exp | atom | column_ref  | ( scalar_exp ) 
atom: parameter | intnum 
subquery: select_exp
select_exp: SELECT name
any_all_some: ANY | ALL | SOME
column_ref: name
parameter: name
intnum: 1
op: + | - | * | / 
comparison: = | < | > 
name: A
