# Ast_Model_Summarize.py

from dataclasses import dataclass

@dataclass
class Program:
	dataset: object
	summary: list
	
@dataclass
class Dataset:
	libname: str
	table: str

@dataclass
class CountOp:
	pass

@dataclass
class MeanOp:
	column: str

@dataclass
class MinOp:
	column: str

@dataclass
class MaxOp:
	column: str

@dataclass
class PeekOp:
	pass

