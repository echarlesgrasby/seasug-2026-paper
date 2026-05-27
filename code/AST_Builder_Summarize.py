# AST_builder_summarize.py

from lark import Transformer
from AST_Model_Summarize import * 


class ASTBuilder(Transformer):
    
    def start(self, items):
        """
        root node
        """
        dataset = items[0]
        summary = items[1]
        
        return Program(
            dataset=dataset,
            summary=summary
        )
    
    def dataset(self, items):
        """
        dataset node -- "which SAS dataset should this map to?"
        """
        libname = str(items[0])
        table = str(items[1])
        
        return Dataset(
            libname=libname,
            table=table
        )
        
    def summary(self, items):
        """
        process the SUMMARY block from the source DSL
        """
        return items

    def count_op(self, items):
        """
        signals that the count operator needs to be present in SQL
        """
        return CountOp()

    def mean_op(self, items):
        """
        return the AVG() of this field
        """
        return MeanOp(
            column=str(items[0])
        )

    def min_op(self, items):
        """
        return the MIN() of this field
        """
        return MinOp(
            column=str(items[0])
        )

    def max_op(self, items):
        """
        return the MAX() of this field
        """
        return MaxOp(
            column=str(items[0])
        )

    def contents_op(self, items):
        """
        signals that a separate call to PROC CONTENTS needs to be created
        """
        return PeekOp()
 