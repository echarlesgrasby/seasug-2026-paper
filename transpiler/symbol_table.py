#================================================================================
#File        : symbol_table.py
#Author      : Eric C. Grasby, MSIQ
#Created     : 2026-07-31
#Dissertation: A Domain-Specific Language Approach to Monitoring and Surveillance in Wholesale Electricity Markets
#Institution : University of Arkansas at Little Rock
#Advisor     : Dr. Daniel Berleant
#--------------------------------------------------------------------------------
#Purpose     :
#   Assembles a compiler-like symbol table that can be used in semantic analysis of underlying input data.
#   The SymbolTable class makes the transpiler aware of dependencies that can't be known during program parsing
#
#Notes       :
#   Note that the Lark grammar and SAS 'emitter' functions are not scoped here. The Symbol table operates purely on the
#   abstract syntax tree from ast_nodes.py
#
#
#Version     : 0.1.0
#Last Updated: 2026-08-20
#================================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ast_nodes import (
    Program,
    CreateDatasetStmt,
    TagStmt,
    SearchStmt,
)


# ---------------------------------------------------------------------------
# Symbol records
# ---------------------------------------------------------------------------

@dataclass
class FieldSymbol:
    """A field of a dataset. Fields are discovered implicitly -- the first
    time a `TAG dataset.field WITH ...` statement mentions one, we record
    it here. (There's no explicit field/schema declaration in the DSL yet;
    """
    name: str
    tags: Dict[str, str] = field(default_factory=dict)
    declared_at_line: Optional[int] = None


@dataclass
class DatasetSymbol:
    name: str
    source_path: str
    tags: Dict[str, str] = field(default_factory=dict)
    fields: Dict[str, FieldSymbol] = field(default_factory=dict)
    declared_at_line: Optional[int] = None

    def get_or_create_field(self, field_name: str, line: Optional[int]) -> FieldSymbol:
        if field_name not in self.fields:
            self.fields[field_name] = FieldSymbol(name=field_name, declared_at_line=line)
        return self.fields[field_name]


@dataclass
class TagIndex:
    """Reverse index: tag name -> every (dataset[.field]) that carries it,
    with the value it was given. This is what a `SEARCH BY TAG(...)`
    statement conceptually queries against, so codegen will likely want
    this shape rather than re-scanning all datasets."""
    entries: Dict[str, List["TagIndexEntry"]] = field(default_factory=dict)

    def add(self, tag_name: str, value: str, dataset_name: str, field_name: Optional[str]):
        self.entries.setdefault(tag_name, []).append(
            TagIndexEntry(dataset_name=dataset_name, field_name=field_name, value=value)
        )


@dataclass
class TagIndexEntry:
    dataset_name: str
    field_name: Optional[str]
    value: str


class SemanticError(Exception):
    """Raised (or just collected, see SymbolTable.errors) for problems that
    are only detectable once you know what's been declared so far -- e.g.
    referencing an undeclared dataset."""

    def __init__(self, message: str, line: Optional[int] = None):
        self.message = message
        self.line = line
        location = f" (line {line})" if line is not None else ""
        super().__init__(f"{message}{location}")


@dataclass
class SymbolTable:
    datasets: Dict[str, DatasetSymbol] = field(default_factory=dict)
    tag_index: TagIndex = field(default_factory=TagIndex)
    errors: List[SemanticError] = field(default_factory=list)
    warnings: List[SemanticError] = field(default_factory=list)

    def add_error(self, message: str, line: Optional[int] = None, rule: Optional[str] = None):
        """Public API for reporting a hard error -- use this from custom
        validators (see validators.py).
        `rule` is an optional short identifier (e.g. "sas-name-
        length") so errors can later be filtered/suppressed by rule name."""
        prefix = f"[{rule}] " if rule else ""
        self.errors.append(SemanticError(f"{prefix}{message}", line))

    def add_warning(self, message: str, line: Optional[int] = None, rule: Optional[str] = None):
        """Same as add_error, but non-fatal -- collected in `warnings`."""
        prefix = f"[{rule}] " if rule else ""
        self.warnings.append(SemanticError(f"{prefix}{message}", line))

    # Kept as thin aliases so the existing internal call sites below don't
    # need to change; new code (including your own validators) should
    # prefer add_error/add_warning.
    _error = add_error
    _warn = add_warning

    def resolve_dataset(self, name: str, line: Optional[int]) -> Optional[DatasetSymbol]:
        ds = self.datasets.get(name)
        if ds is None:
            self.add_error(f"Reference to undefined dataset '{name}'", line, rule="undefined-dataset")
        return ds

    def all_dataset_names(self) -> List[str]:
        """Convenience for validators that need to scan every dataset."""
        return list(self.datasets.keys())


def build_symbol_table(program: Program) -> SymbolTable:
    table = SymbolTable()

    for stmt in program.statements:
        if isinstance(stmt, CreateDatasetStmt):
            _handle_create(table, stmt)
        elif isinstance(stmt, TagStmt):
            _handle_tag(table, stmt)
        elif isinstance(stmt, SearchStmt):
            _handle_search(table, stmt)
        else:
            table._error(f"Unhandled statement type: {type(stmt).__name__}", stmt.line)

    return table


def _handle_create(table: SymbolTable, stmt: CreateDatasetStmt) -> None:
    if stmt.name in table.datasets:
        table.add_error(f"Dataset '{stmt.name}' is already defined "
                         f"(originally at line {table.datasets[stmt.name].declared_at_line})",
                         stmt.line, rule="duplicate-dataset")
        return
    table.datasets[stmt.name] = DatasetSymbol(
        name=stmt.name,
        source_path=stmt.source.path,
        declared_at_line=stmt.line,
    )


def _handle_tag(table: SymbolTable, stmt: TagStmt) -> None:
    target = stmt.target
    dataset = table.resolve_dataset(target.dataset_name, stmt.line)
    if dataset is None:
        return  # error already recorded

    if target.is_field_target:
        field_sym = dataset.get_or_create_field(target.field_name, stmt.line)
        for pair in stmt.pairs:
            field_sym.tags[pair.key] = pair.value
            table.tag_index.add(pair.key, pair.value, dataset.name, target.field_name)
    else:
        for pair in stmt.pairs:
            dataset.tags[pair.key] = pair.value
            table.tag_index.add(pair.key, pair.value, dataset.name, None)


def _handle_search(table: SymbolTable, stmt: SearchStmt) -> None:
    if stmt.tag_name not in table.tag_index.entries:
        table.add_warning(
            f"SEARCH BY TAG(\"{stmt.tag_name}\") references a tag that is "
            f"never assigned anywhere in this script",
            stmt.line,
            rule="search-unknown-tag",
        )
