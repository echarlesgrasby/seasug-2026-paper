#================================================================================
#File        : ast_nodes.py
#Author      : Eric C. Grasby, MSIQ
#Created     : 2026-07-31
#Dissertation: A Domain-Specific Language Approach to Monitoring and Surveillance in Wholesale Electricity Markets
#Institution : University of Arkansas at Little Rock
#Advisor     : Dr. Daniel Berleant
#--------------------------------------------------------------------------------
#Purpose     :
#    Functions as a basic registry of all valid abstract syntax tree nodes that can be created
#    from the mlang grammar
#
#Notes       :
#    Every node is a plain dataclass. Embeds `line`/`column` metadata so that the transpiler is aware of
#    where the code came from in the source "program"
#    This enables the transformer to convert from mlang --> SAS (or whatever target language)
#
#Version     : 0.1.0
#Last Updated: 2026-08-20
#================================================================================

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Node:
    """Base class for all AST nodes. Holds source-position metadata."""
    line: Optional[int] = field(default=None, repr=False, compare=False)
    column: Optional[int] = field(default=None, repr=False, compare=False)


# ---------------------------------------------------------------------------
# Top level
# ---------------------------------------------------------------------------

@dataclass
class Program(Node):
    statements: List["Statement"] = field(default_factory=list)


# A Statement is just a type alias for readability; any of the below
# concrete statement nodes may appear in Program.statements.
Statement = "CreateDatasetStmt | TagStmt | SearchStmt"


# ---------------------------------------------------------------------------
# CREATE DATASET name FROM CSV("path");
# ---------------------------------------------------------------------------

@dataclass
class CsvSource(Node):
    """The FROM CSV(...) clause. Only source type supported for now, but
    kept as its own node so that adding
    JSON/PARQUET/etc. later doesn't require touching CreateDatasetStmt."""
    path: str = ""
    type: str = "CSV"


@dataclass
class CreateDatasetStmt(Node):
    name: str = ""
    source: CsvSource = None


# ---------------------------------------------------------------------------
# TAG target WITH key = "value";
# TAG target WITH (key1 = "value1", key2 = "value2");
# ---------------------------------------------------------------------------

@dataclass
class Target(Node):
    """Reference to either a whole dataset (`dataset`) or a specific field
    on a dataset (`dataset.field`). `field_name` is None for the former."""
    dataset_name: str = ""
    field_name: Optional[str] = None

    @property
    def is_field_target(self) -> bool:
        return self.field_name is not None

    def __str__(self) -> str:
        if self.field_name:
            return f"{self.dataset_name}.{self.field_name}"
        return self.dataset_name


@dataclass
class TagPair(Node):
    key: str = ""
    value: str = ""


@dataclass
class TagStmt(Node):
    target: Target = None
    pairs: List[TagPair] = field(default_factory=list)


# ---------------------------------------------------------------------------
# SEARCH BY TAG(name) THEN ORDER BY ASC;
# ---------------------------------------------------------------------------

@dataclass
class OrderClause(Node):
    direction: str = "ASC"  # "ASC" | "DESC"


@dataclass
class SearchStmt(Node):
    tag_name: str = ""
    order: Optional[OrderClause] = None
