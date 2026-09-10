#================================================================================
#File        : ast_printer.py
#Author      : Eric C. Grasby, MSIQ
#Created     : 2026-07-31
#Dissertation: A Domain-Specific Language Approach to Monitoring and Surveillance in Wholesale Electricity Markets
#Institution : University of Arkansas at Little Rock
#Advisor     : Dr. Daniel Berleant
#--------------------------------------------------------------------------------
#Purpose     :
#    Visits the abstract syntax tree created by the transpiler and prints it to the log in plaintext format
#Notes       :
#    This is useful when debugging or documenting what an .mlang script parses into
#
#Usage:
#    from ast_printer import format_ast
#    print(format_ast(program))
#
#    # ASCII fallback if unicode box-drawing characters cannot be printed:
#    print(format_ast(program, style="ascii"))
#
#
#Version     : 0.1.0
#Last Updated: 2026-08-24
#================================================================================

import dataclasses
from typing import Any

_SCALAR_TYPES = (str, int, float, bool, type(None))

_CONNECTORS = {
    "unicode": {"branch": "├── ", "last": "└── ", "pipe": "│   ", "blank": "    "},
    "ascii":   {"branch": "|-- ", "last": "`-- ", "pipe": "|   ", "blank": "    "},
}


def _is_dataclass_instance(obj: Any) -> bool:
    return dataclasses.is_dataclass(obj) and not isinstance(obj, type)


def _is_scalar(obj: Any) -> bool:
    return isinstance(obj, _SCALAR_TYPES)


def _scalar_repr(obj: Any) -> str:
    return f'"{obj}"' if isinstance(obj, str) else repr(obj)


def _node_label(node: Any) -> str:
    """One-line label: ClassName(scalar=val, ...) for dataclasses,
    '[N]' for lists, or a plain repr for scalars."""
    if _is_dataclass_instance(node):
        cls = type(node).__name__
        scalars = [
            f"{f.name}={_scalar_repr(getattr(node, f.name))}"
            for f in dataclasses.fields(node)
            if _is_scalar(getattr(node, f.name))
        ]
        return f"{cls}({', '.join(scalars)})" if scalars else cls
    if isinstance(node, list):
        return f"[{len(node)}]" if node else "[] (empty)"
    return _scalar_repr(node)


def _child_entries(node: Any):
    """(label, value) pairs for recursive pairs (e.g. list elements)
    """
    if _is_dataclass_instance(node):
        return [
            (f.name, getattr(node, f.name))
            for f in dataclasses.fields(node)
            if not _is_scalar(getattr(node, f.name))
        ]
    if isinstance(node, list):
        return [(f"[{i}]", item) for i, item in enumerate(node)]
    return []


def format_ast(node: Any, style: str = "unicode") -> str:
    """Render `node` (any AST dataclass, or a whole Program) as an indented
    tree string. `style` is 'Unicode' (default, box-drawing chars) or
    'ASCII' (plain characters) as a fallback."""
    conn = _CONNECTORS[style]
    lines = []
    _render(node, field_label=None, prefix="", is_last=True, is_root=True,
             lines=lines, conn=conn)
    return "\n".join(lines)


def _render(node, field_label, prefix, is_last, is_root, lines, conn):
    label = _node_label(node)
    if field_label is not None:
        label = f"{field_label}: {label}"

    connector = "" if is_root else (conn["last"] if is_last else conn["branch"])
    lines.append(prefix + connector + label)

    child_prefix = prefix if is_root else prefix + (conn["blank"] if is_last else conn["pipe"])
    entries = _child_entries(node)
    for i, (child_label, child_val) in enumerate(entries):
        _render(child_val, child_label, child_prefix, i == len(entries) - 1,
                 False, lines, conn)
