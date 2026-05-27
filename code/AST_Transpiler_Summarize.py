# AST_Transpiler_Summarize.py

from AST_Model_Summarize import *

class SASSummarizeTranspiler:
    
    def transpile(self, program):
        
        sql_snippets = []
        nonsql_snippets = []
        
        for summ_tree in program.summary:
            operator = summ_tree.children[0]
            if isinstance(operator, CountOp):
                
                sql_snippets.append(
                    "COUNT(1) AS ROW_COUNT"
                )
            elif isinstance(operator, MeanOp):
                sql_snippets.append(
                    f"AVG({operator.column}) AS AVG_{operator.column}"
                )
            elif isinstance(operator, MinOp):
                sql_snippets.append(
                    f"MIN({operator.column}) AS MIN_{operator.column}"
                )
            elif isinstance(operator, MaxOp):
                sql_snippets.append(
                    f"MAX({operator.column}) AS MAX_{operator.column}"
                )
            elif isinstance(operator, PeekOp):
                nonsql_snippets.append(
                    f"""
                    PROC CONTENTS DATA={program.dataset.libname}.{program.dataset.table}; RUN;
                    """
                )
        
        
        output_sas_code = ""
        sql = ""
        nonsql = ""
        if len(sql_snippets) > 0:
            select_clause = ",\n        ".join(sql_snippets)
            sql = f"""
            PROC SQL;
                CREATE TABLE WORK.DATASET_FROM_DSL AS
                SELECT {select_clause}
                FROM {program.dataset.libname}.{program.dataset.table};
            QUIT;
            """;
        else:
            print(sql_snippets)
        if len(nonsql_snippets) > 0:
            nonsql = "\n\n".join(nonsql_snippets)
        else:
            print(sql_snippets)
            
        output_sas_code = sql + nonsql
        print(f"Output SAS code is {output_sas_code}")
        return output_sas_code