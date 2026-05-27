# test_parser_and_transpiler.py

from lark import Lark
from AST_Builder_Summarize import ASTBuilder
from AST_Transpiler_Summarize import SASSummarizeTranspiler

# import the summarize_dataset.lark file
with open("summarize_dataset.lark") as g:
	grammar = g.read()

# create a parser according to the summarize_dataset.lark rules 
parser = Lark(grammar, parser="lalr")

# load the sample DSL code
with open("summarize.mlang") as ff:
	source = ff.read()

# parse it!
tree = parser.parse(source)

# pretty print the parse tree
print(tree.pretty())


# create the abstract syntax tree (AST) from the parse tree
ast = ASTBuilder().transform(tree)

print(ast)

# now lets create a basic transpiler
transpiler = SASSummarizeTranspiler()

sas_code = transpiler.transpile(ast)
