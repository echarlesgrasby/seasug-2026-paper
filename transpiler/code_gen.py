"""
Code generation scaffold.

This module defines the *interface* between the semantically-analyzed
program (AST + SymbolTable) and actual SAS output.

Design:
  - `CodeGenerator` is an abstract base class with one method per AST node
    kind that produces code, plus a driver (`generate`) that walks the
    Program in order and dispatches to the right method. No separate Visitor
    class right now since the AST is small and flat.
  - Each `emit_*` method receives both the AST node *and* the SymbolTable,
    to allow access to resolved information (e.g. a tag_stmt's method
    can look up `symbols.datasets[...]` to see all tags collected so far,
    not just the ones on this statement) if SAS generation needs
    fuller context than a single statement provides.
  - `CodeGenError` raise from within emit_* methods
    for anything that's a valid AST/symbol table but can't be lowered to
    SAS (e.g. an unsupported source type beyond CSV inputs).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ast_nodes import (
    Program,
    CreateDatasetStmt,
    TagStmt,
    SearchStmt,
)
from symbol_table import SymbolTable


class CodeGenError(Exception):
    """Raised by a CodeGenerator implementation when a construct that is
    semantically valid can't be lowered to output code for some reason
    (unsupported feature, generator-specific restriction, etc.)."""

    def __init__(self, message: str, line: int = None):
        self.message = message
        self.line = line
        location = f" (line {line})" if line is not None else ""
        super().__init__(f"{message}{location}")


class CodeGenerator(ABC):
    """Abstract base for a target-language backend.

    Subclass this (e.g. `SasCodeGenerator`) and implement each `emit_*`
    method to return the string(s) of output code for that statement.
    `generate()` handles walking the program and joining the results --
    should not require a direct override
    """

    def generate(self, program: Program, symbols: SymbolTable) -> str:
        """Drives codegen over the whole program, in source order, and
        returns the final generated output as a single string."""
        chunks: List[str] = []
        chunks.extend(self.preamble(symbols))

        for stmt in program.statements:
            if isinstance(stmt, CreateDatasetStmt):
                chunks.append(self.emit_create_dataset(stmt, symbols))
            elif isinstance(stmt, TagStmt):
                try:
                    chunks.append(self.emit_tag(stmt, symbols))
                except Exception as ex:
                    raise CodeGenError(f"Cannot find template file for tag generation: {ex}",
                                        getattr(stmt, "line", None),
                    )
            elif isinstance(stmt, SearchStmt):
                chunks.append(self.emit_search(stmt, symbols))
            else:
                raise CodeGenError(
                    f"No codegen handler for statement type {type(stmt).__name__}",
                    getattr(stmt, "line", None),
                )

        chunks.extend(self.postamble(symbols))
        return "\n".join(chunk for chunk in chunks if chunk)

    # -- Hooks for boilerplate that isn't tied to a specific statement -----

    @abstractmethod
    def preamble(self, symbols: SymbolTable) -> List[str]:
        """Optional: code to emit once, before any statement output (e.g.
        SAS `OPTIONS`/`LIBNAME` setup). Default: nothing."""
        raise NotImplementedError

    @abstractmethod
    def postamble(self, symbols: SymbolTable) -> List[str]:
        """Optional: code to emit once, after all statement output (e.g.
        cleanup, `RUN;`/`QUIT;`). Default: nothing."""
        raise NotImplementedError

    # -- Required per-statement emitters -----------------------------------

    @abstractmethod
    def emit_create_dataset(self, stmt: CreateDatasetStmt, symbols: SymbolTable) -> str:
        """Emit output code for a single CREATE DATASET ... FROM CSV(...);
        statement. `symbols.datasets[stmt.name]` holds the fully-resolved
        DatasetSymbol
        """
        raise NotImplementedError

    @abstractmethod
    def emit_tag(self, stmt: TagStmt, symbols: SymbolTable) -> str:
        """Emit output code for a single TAG ... WITH ...; statement.
        Note tags may not correspond to *any* runtime SAS step at all
        (e.g. if you're tracking them purely in a metadata table) --
        returning "" is fine if there's nothing to emit here."""
        raise NotImplementedError

    @abstractmethod
    def emit_search(self, stmt: SearchStmt, symbols: SymbolTable) -> str:
        """Emit output code for a single SEARCH BY TAG(...) [THEN ORDER BY
        ASC|DESC]; statement. `symbols.tag_index.entries[stmt.tag_name]`
        gives every dataset/field that carries this tag, pre-resolved.
        """
        raise NotImplementedError


class NullCodeGenerator(CodeGenerator):
    """Trivial placeholder implementation so the pipeline is runnable
    end-to-end as a stub
    """

    def preamble(self, symbols: SymbolTable) -> List[str]:
        return ["/* --- generated by DSL transpiler (NullCodeGenerator) --- */"]

    def emit_create_dataset(self, stmt: CreateDatasetStmt, symbols: SymbolTable) -> str:
        return f'/* CREATE DATASET {stmt.name} FROM CSV("{stmt.source.path}") */'

    def emit_tag(self, stmt: TagStmt, symbols: SymbolTable) -> str:
        pairs = ", ".join(f'{p.key}="{p.value}"' for p in stmt.pairs)
        return f"/* TAG {stmt.target} WITH {pairs} */"

    def emit_search(self, stmt: SearchStmt, symbols: SymbolTable) -> str:
        order = f" THEN ORDER BY {stmt.order.direction}" if stmt.order else ""
        return f'/* SEARCH BY TAG("{stmt.tag_name}"){order} */'

    def postamble(self, symbols: SymbolTable) -> List[str]:
        return [" /* --- end of DSL code (NullCodeGenerator) --- */"]

