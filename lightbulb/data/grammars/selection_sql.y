S: main
main: selection_options
selection_options: options_exp function_ref | function_ref 
function_ref: function_exp ( name )
function_exp: LOAD_FILE | AES_ENCRYPT | AES_DECRYPT | ASYMMETRIC_ENCRYPT | ASYMMETRIC_SIGN | ASYMMETRIC_VERIFY | RLIKE
options_exp: ALL | DISTINCT | DISTINCTROW | HIGH_PRIORITY | STRAIGHT_JOIN | SQL_SMALL_RESULT | SQL_BIG_RESULT | SQL_BUFFER_RESULT | SQL_CACHE | SQL_NO_CACHE | SQL_CALC_FOUND_ROWS
name: A
