"""
Custom semantic validators.

The core `symbol_table.py` build step only enforces rules the *language*
itself needs (no duplicate datasets, no undefined references) -- it knows
nothing about SAS. Everything target-specific (identifier length limits,
illegal characters, reserved words, path constraints, whatever else comes
up) belongs here instead, as small independent validator functions that
run *after* the symbol table is fully built.

Why a separate pass instead of stuffing checks into symbol_table.py:
  - Keeps "what does this program mean" (symbol_table.py) separate from
    "is this program legal for MY target" (here). If you ever generate
    something other than SAS, symbol_table.py doesn't change at all.
  - Each rule is independently testable/toggleable -- you can run a
    subset in unit tests, or disable one without touching the others.
  - Validators see the *complete* SymbolTable (all datasets, all fields,
    the tag index), so they can check things a single-statement handler
    in symbol_table.py can't easily see -- e.g. "do any two datasets
    collide once truncated to 32 characters?"

How to add a new rule: write a function `(table: SymbolTable) -> None`
that inspects `table` and calls `table.add_error(...)` / `add_warning(...)`
for anything it finds, then add it to DEFAULT_VALIDATORS at the bottom
(or pass your own list into run_validators explicitly).
"""

from __future__ import annotations

import re
from typing import Callable, List
from peek_data_file import peek_data_file
from symbol_table import SymbolTable

Validator = Callable[[SymbolTable], None]


# ---------------------------------------------------------------------------
# SAS identifier rules
# ---------------------------------------------------------------------------
#
# These encode real SAS naming constraints:
#   - Names (datasets, variables/fields) are limited to 32 characters.
#   - Must start with a letter or underscore; remaining chars are
#     letters/digits/underscores only -- no spaces, no punctuation.
#   - A handful of words are reserved/special and shouldn't be used as
#     dataset or variable names even though SAS won't always hard-reject
#     them (e.g. they can shadow automatic variables).
#
# Adjust/extend freely -- these are meant as a starting point you can
# tune to whatever your actual SAS environment enforces.

SAS_MAX_NAME_LENGTH = 32
SAS_VALID_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SAS_RESERVED_WORDS = {
    "_all_", "_character_", "_infile_", "_n_", "_null_", "_numeric_",
    "data", "input", "output", "proc", "run", "set", "then", "else",
}


def _check_sas_name(table: SymbolTable, name: str, line, kind: str, rule: str) -> None:
    """Shared logic for validating a single identifier destined to become
    a SAS dataset name or variable name. `kind` is just for message text
    (e.g. "dataset", "field")."""
    if len(name) > SAS_MAX_NAME_LENGTH:
        table.add_error(
            f"{kind.capitalize()} name '{name}' is {len(name)} characters long; "
            f"SAS names must be {SAS_MAX_NAME_LENGTH} characters or fewer",
            line, rule=f"{rule}-length",
        )

    if " " in name:
        table.add_error(
            f"{kind.capitalize()} name '{name}' contains spaces, which SAS "
            f"names cannot contain",
            line, rule=f"{rule}-spaces",
        )
    elif not SAS_VALID_NAME_RE.match(name):
        table.add_error(
            f"{kind.capitalize()} name '{name}' is not a valid SAS identifier "
            f"(must start with a letter or underscore, and contain only "
            f"letters, digits, and underscores)",
            line, rule=f"{rule}-charset",
        )

    if name.lower() in SAS_RESERVED_WORDS:
        table.add_warning(
            f"{kind.capitalize()} name '{name}' shadows a SAS reserved word",
            line, rule=f"{rule}-reserved-word",
        )

def _check_source_field_names(table: SymbolTable, name: str, line, kind: str, rule: str) -> None:
    """Validate discovered field names within CSV files to ensure that they comply with
     SAS field naming requirements.
    """
    pass

def check_dataset_names(table: SymbolTable) -> None:
    """Validates every CREATE DATASET name against SAS naming rules."""
    for ds in table.datasets.values():
        _check_sas_name(table, ds.name, ds.declared_at_line, "dataset", "sas-dataset-name")


def check_field_names(table: SymbolTable) -> None:
    """Validates every discovered field name (these become SAS variable
    names) against the same rules."""
    for ds in table.datasets.values():
        for f in ds.fields.values():
            _check_sas_name(table, f.name, f.declared_at_line, "field", "sas-field-name")


def check_field_names_in_data_files(table: SymbolTable) -> None:
    """Validates discovered field names in data files to ensure that they align
    with required SAS variable names
    """
    for ds in table.datasets.values():
        field_names = peek_data_file(ds.source_path, ds.name)
        check_source_field_name_collisions_when_truncated(table, ds.name, field_names)

        for field_name in field_names:
            _check_sas_name(table, field_name, ds.declared_at_line, "field", "source-data-field-name")


def check_dataset_name_collisions_when_truncated(table: SymbolTable) -> None:
    """SAS silently truncates over-length names rather than always hard
    failing in every context -- so two DSL dataset names that are both
    under some external limit but identical in their first 32 chars could
    collide once lowered to SAS. Catches that class of bug independent of
    the plain length check above."""
    seen = {}
    for ds in table.datasets.values():
        truncated = ds.name[:SAS_MAX_NAME_LENGTH].lower()
        if truncated in seen and seen[truncated] != ds.name:
            table.add_error(
                f"Dataset names '{seen[truncated]}' and '{ds.name}' collide "
                f"once truncated to {SAS_MAX_NAME_LENGTH} characters",
                ds.declared_at_line, rule="sas-dataset-name-collision",
            )
        seen.setdefault(truncated, ds.name)

def check_source_field_name_collisions_when_truncated(table: SymbolTable, ds_name: str, field_names: List[str]) -> None:
    """
    Similar logic to `check_dataset_name_collisions_when_truncated` but applies the logic
    to field names within a dataset, which should also not be duplicated
    """
    seen = {}
    for field_name in field_names:
        truncated = field_name[:SAS_MAX_NAME_LENGTH].lower()
        if truncated in seen and seen[truncated] != field_name:
            table.add_error(
                f"Field names '{seen[truncated]}' and '{field_name}' in data set '{ds_name}' collide "
                f"once truncated to {SAS_MAX_NAME_LENGTH} characters",
                None, rule="source"
            )
        seen.setdefault(truncated, field_name)

# ---------------------------------------------------------------------------
# File path rules
# ---------------------------------------------------------------------------

def check_source_path_extension(table: SymbolTable) -> None:
    """Since only CSV sources are supported right now, flag anything that
    doesn't look like a .csv file -- easy to catch a typo'd path early
    rather than have SAS fail confusingly at runtime."""
    for ds in table.datasets.values():
        if not ds.source_path.lower().endswith(".csv"):
            table.add_warning(
                f"Source path '{ds.source_path}' for dataset '{ds.name}' "
                f"does not end in .csv",
                ds.declared_at_line, rule="source-path-extension",
            )


# ---------------------------------------------------------------------------
# Registry + runner
# ---------------------------------------------------------------------------

DEFAULT_VALIDATORS: List[Validator] = [
    check_dataset_names,
    check_field_names,
    check_field_names_in_data_files,
    check_dataset_name_collisions_when_truncated,
    check_source_path_extension,

]


def run_validators(table: SymbolTable, validators: List[Validator] = None) -> None:
    """Runs each validator against the (already-built) symbol table.
    Validators report problems by calling table.add_error/add_warning
    themselves -- this function doesn't return anything; check
    table.errors / table.warnings afterward.

    Pass a custom `validators` list (e.g. a subset, or with your own
    rules appended) to override DEFAULT_VALIDATORS -- useful in tests, or
    if you want different rule sets for different environments.
    """
    for validator in (validators if validators is not None else DEFAULT_VALIDATORS):
        validator(table)
