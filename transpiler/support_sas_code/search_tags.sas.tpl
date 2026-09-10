title "Results of Tag Search: %sysfunc(datetime(), datetime20.)";

PROC SQL;
select * from
(
select v1.libname as "Library"n, v1.memname as "Data Set"n, v1.name as "Column Name"n, v1.xattr as "Tag Name"n
from sashelp.vxattr v1
where upper(v1.xattr) = '{{TAG_NAME}}'
and v1.name is null
union all
select v2.libname as "Library"n, v2.memname as "Data Set"n, v2.name as "Column Name"n, v2.xattr as "Tag Name"n
from sashelp.vxattr v2
where upper(v2.xattr) = '{TAG_NAME}'
and v2.name is not null
) ORDER BY "Library"n {{ORDER_DIR}}, "Data Set"n {{ORDER_DIR}}, "Column Name"n {{ORDER_DIR}}, "Tag Name"n {{ORDER_DIR}};
QUIT;

ods noproctitle;