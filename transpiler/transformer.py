"""
Parse-tree -> AST transformation.

This is the only module that should import both `lark` and `ast_nodes`.
Everything downstream of this module works purely in terms of ast_nodes,
so the rest of the pipeline stays decoupled from grammar/parser details.
"""

from __future__ import annotations

from lark import Lark, Transformer, v_args, LarkError, UnexpectedCharacters
from lark.tree import Meta
import logging

from ast_nodes import (
    Program,
    CsvSource,
    CreateDatasetStmt,
    Target,
    TagPair,
    TagStmt,
    OrderClause,
    SearchStmt,
)

logger = logging.getLogger(__name__)

def _unquote(string_token) -> str:
    """STRING tokens include their surrounding double quotes and may contain
    escape sequences; this strips the quotes and resolves \\" and \\\\."""
    text = str(string_token)
    inner = text[1:-1]
    return inner.replace('\\"', '"').replace("\\\\", "\\")


@v_args(meta=True)
class DslTransformer(Transformer):
    """Walks the Lark parse tree bottom-up, building ast_nodes.* objects.

    `v_args(meta=True)` gives every rule method a `meta` (line/column info)
    as the first argument, ahead of the transformed children -- that's how
    we attach source positions to AST nodes for later diagnostics.
    """

    def start(self, meta: Meta, children):
        return Program(statements=list(children), line=1, column=1)

    def statement(self, meta: Meta, children):
        # statement is a pure alternation; unwrap to the single child.
        return children[0]

    # -- CREATE DATASET ------------------------------------------------

    def create_dataset_stmt(self, meta: Meta, children):
        name_tok, source = children
        return CreateDatasetStmt(
            name=str(name_tok),
            source=source,
            line=meta.line,
            column=meta.column,
        )

    def source(self, meta: Meta, children):
        (path_tok,) = children
        return CsvSource(path=_unquote(path_tok), line=meta.line, column=meta.column)

    # -- TAG -------------------------------------------------------------

    def target(self, meta: Meta, children):
        if len(children) == 1:
            return Target(dataset_name=str(children[0]), field_name=None,
                          line=meta.line, column=meta.column)
        dataset_tok, field_tok = children
        return Target(dataset_name=str(dataset_tok), field_name=str(field_tok),
                      line=meta.line, column=meta.column)

    def tag_pair(self, meta: Meta, children):
        key_tok, value_tok = children
        return TagPair(key=str(key_tok), value=_unquote(value_tok),
                       line=meta.line, column=meta.column)

    def tag_body(self, meta: Meta, children):
        # Either a single tag_pair, or several (parenthesized form) -- in
        # both cases children are already-transformed TagPair nodes.
        return list(children)

    def tag_stmt(self, meta: Meta, children):
        target, pairs = children
        return TagStmt(target=target, pairs=pairs, line=meta.line, column=meta.column)

    # -- SEARCH ------------------------------------------------------------

    def asc(self, meta: Meta, children):
        return OrderClause(direction="ASC", line=meta.line, column=meta.column)

    def desc(self, meta: Meta, children):
        return OrderClause(direction="DESC", line=meta.line, column=meta.column)

    def order_clause(self, meta: Meta, children):
        (direction,) = children
        return direction

    def search_stmt(self, meta: Meta, children):
        tag_name_tok, order = children
        return SearchStmt(
            tag_name=str(tag_name_tok),
            order=order,
            line=meta.line,
            column=meta.column,
        )


def build_parser() -> Lark:
    with open("grammar.lark", "r", encoding="utf-8") as f:
        grammar_text = f.read()
    # propagate_positions=True is required for `meta.line`/`meta.column`
    # to be populated on every rule node above.
    return Lark(grammar_text, parser="lalr", propagate_positions=True)


def parse_to_ast(source_text: str) -> Program:
    """Full front-end pipeline: DSL source text -> Program AST."""
    parser = build_parser()
    try:
        tree = parser.parse(source_text)
        return DslTransformer().transform(tree)
    except UnexpectedCharacters as uec:
        logging.error(f"Unexpected character '{uec.char}' found in input at line {uec.line}, column {uec.column}.")
    except LarkError as lke:
        logging.error(f"Error occurred processing input file according to grammar.lark: {lke}")
    raise Exception("Cannot continue processing.")