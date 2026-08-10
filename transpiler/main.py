#================================================================================
#File        : main.py
#Author      : Eric C. Grasby, MSIQ
#Created     : 2026-07-31
#Dissertation: A Domain-Specific Language Approach to Monitoring and Surveillance in Wholesale Electricity Markets
#Institution : University of Arkansas at Little Rock
#Advisor     : Dr. Daniel Berleant
#--------------------------------------------------------------------------------
#Purpose     :
#    This serves as the driver program for the Mlang transpiler. All transpiler operations are called through this
#    script. Pipeline driver: DSL Source --> AST --> SymbolTable --> generated code & log files
#
#Notes       :
#    see `parse_command_line_arguments` for input args
#
#
#Version     : 0.1.0
#Last Updated: 2026-07-31
#================================================================================

"""
Pipeline driver: DSL source -> AST -> SymbolTable -> generated code & log files

Run directly for a demo against sample.mlang:
    python main.py sample.mlang
"""

from __future__ import annotations

import sys
import logging
import argparse

from pprint import pformat
from transformer import parse_to_ast
from symbol_table import build_symbol_table
from validators import run_validators
from code_gen import NullCodeGenerator
import run as RunManager
import sas_code_generator


def setup_logging(level=logging.INFO) -> None:
    logging.basicConfig(level=level,
                        format="%(asctime)s - %(levelname)-8s - %(name)s: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        stream=sys.stdout
    )

def parse_command_line_arguments() -> None:
    parser = argparse.ArgumentParser(description="A command-line transpiler to convert .mlang files to .sas code")
    parser.add_argument("--debug", action="store_false", help="Run transpiler in debug mode")
    parser.add_argument("--input_file", default="sample.dsl", help="Input .dsl file")
    parser.add_argument()

def compile_source(source_text: str, generator=None, validators=None) -> tuple:
    """Runs the full pipeline and returns (program, symbols, output_code).

    Raises on parse errors (from Lark) or if the symbol table collected
    any hard errors -- either from the core language checks in
    symbol_table.py (undefined dataset, duplicate dataset, ...) or from
    the custom target-specific rules in validators.py (SAS name length,
    illegal characters, ...). Semantic errors are non-fatal to *collect*,
    but you generally don't want to hand a program with errors to codegen.

    Pass `validators=[...]` to override the default rule set (see
    validators.run_validators); pass `validators=[]` to skip custom
    validation entirely and only run the core language checks.
    """
    validators = []
    program = parse_to_ast(source_text)
    symbols = build_symbol_table(program)
    run_validators(symbols, validators)

    if symbols.errors:
        messages = "\n".join(f"  - {e}" for e in symbols.errors)
        logging.error(f"Semantic errors found:\n{messages}")

    generator = generator or NullCodeGenerator()
    output_code = generator.generate(program, symbols)
    return program, symbols, output_code


def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    current_run = RunManager.Run(datetime_string="2026_08_10_15_53_00")

    print("=" * 70)
    logger.info("Running mlang transpiler...")
    print("=" * 70)


    path = sys.argv[1] if len(sys.argv) > 1 else "sample.mlang"
    with open(path, "r", encoding="utf-8") as f:
        source_text = f.read()

    code_generator = sas_code_generator.SASCodeGenerator()
    program, symbols, output_code = compile_source(source_text, generator=code_generator)

    #if debug: # print out the AST
    #print("=" * 70)
    #print("AST")
    #print("=" * 70)
    #for stmt in program.statements:
    #    print(pformat(stmt, width=100))

    # if debug: # print out the Symbol Table
    #print()
    #print("=" * 70)
    #print("SYMBOL TABLE")
    #print("=" * 70)
    #for name, ds in symbols.datasets.items():
    #    print(f"Dataset: {name}")
    #    print(f"  source_path = {ds.source_path!r}")
    #    print(f"  tags        = {ds.tags}")
    #    for fname, fsym in ds.fields.items():
    #        print(f"  field {fname}: tags = {fsym.tags}")

    # Notify the user if there are any warnings that were detected during transpilation
    if symbols.warnings:
        print()
        print("Warnings:")
        for w in symbols.warnings:
            print(f"  - {w}")

    if len(symbols.errors) == 0:
        print("=" * 70)
        print("Output Code")
        print("=" * 70)
        print(output_code)
    else:
        logger.error(f"{len(symbols.errors)} error(s) found during transpiler process. Please investigate these errors "
                     f"and adjust your mlang program. \nErrors can be found in: {current_run.current_run_path}")

    print("=" * 70)
    logger.info("Exiting transpiler.")
    print("=" * 70)

if __name__ == "__main__":
    main()
