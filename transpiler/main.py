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
from argparse import Namespace
from pathlib import Path

from pprint import pformat
from transformer import parse_to_ast
from symbol_table import build_symbol_table
from validators import run_validators
from code_gen import NullCodeGenerator
from run import Run as RunManager
import sas_code_generator


def setup_logging(level=logging.INFO) -> None:
    logging.basicConfig(level=level,
                        format="%(asctime)s - %(levelname)-8s - %(name)s: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        stream=sys.stdout
    )

def parse_command_line_arguments() -> Namespace:
    """
    Handles any user-defined command line arguments
    """
    #program_description = """
    #A command-line transpiler to convert .mlang files to .sas code.
    #Author: Eric C. Grasby, MSIQ
    #
    #                         ████
    #                    ░░███
    #     █████████████   ░███   ██████   ████████    ███████
    #    ░░███░░███░░███  ░███  ░░░░░███ ░░███░░███  ███░░███
    #     ░███ ░███ ░███  ░███   ███████  ░███ ░███ ░███ ░███
    #     ░███ ░███ ░███  ░███  ███░░███  ░███ ░███ ░███ ░███
    #     █████░███ █████ █████░░████████ ████ █████░░███████
    #    ░░░░░ ░░░ ░░░░░ ░░░░░  ░░░░░░░░ ░░░░ ░░░░░  ░░░░░███
    #                                                ███ ░███
    #                                               ░░██████
    #                                                 ░░░░░░
    #
    #This program is in support of the author's dissertation work.
    #See https://github.com/echarlesgrasby/seasug-2026-paper for the source code.
    #"""

    program_description = """
    A command-line transpiler to convert .mlang files to .sas code.
    Author: Eric C. Grasby, MSIQ
    
    This program is in support of the author's dissertation work. 
    See https://github.com/echarlesgrasby/seasug-2026-paper
    """

    parser = argparse.ArgumentParser(description=program_description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--input_file", required=True, help="Input .mlang DSL file")
    parser.add_argument("--run_dir", type=str, default=None, help="Overwrite existing run directory with specified date string")

    # User can only provide one of these flags to set the log level
    log_level_args = parser.add_mutually_exclusive_group(required=False) # if False, program will assume INFO
    log_level_args.add_argument("--debug", action="store_true", help="Run transpiler in debug mode")
    log_level_args.add_argument("--warn", action="store_true", help="Run transpiler in warn mode")
    log_level_args.add_argument("--error", action="store_true", help="Run transpiler in report error mode")

    return parser.parse_args()


def compile_source(source_text: str, generator=None, validators=None, **kwargs) -> tuple:
    """Runs the full pipeline and returns (program, symbols, output_code).

    Raises on parse errors (from Lark) or if the symbol table collected
    any hard errors -- either from the core language checks in
    symbol_table.py (undefined dataset, duplicate dataset, ...) or from
    the custom target-specific rules in validators.py (SAS name length,
    illegal characters, ...). Semantic errors are non-fatal to *collect*,
    but typically need to be handled before generating code.

    Pass `validators=[...]` to override the default rule set (see
    validators.run_validators); pass `validators=[]` to skip custom
    validation entirely and only run the core language checks.
    """
    program = parse_to_ast(source_text)
    symbols = build_symbol_table(program)
    run_validators(symbols)

    if symbols.errors:
        messages = "\n".join(f"  - {e}" for e in symbols.errors)
        logging.error(f"Semantic errors found:\n{messages}")

    generator = generator or NullCodeGenerator()
    output_code = generator.generate(program, symbols, current_run=kwargs.get("current_run"))
    return program, symbols, output_code


def main() -> None:
    args = parse_command_line_arguments()

    if args.debug:
        lvl = logging.DEBUG
    elif args.warn:
        lvl = logging.WARNING
    elif args.error:
        lvl = logging.ERROR
    else:
        lvl = logging.INFO
    setup_logging(level=lvl)
    logger = logging.getLogger(__name__)

    run_dir_name = None
    if args.run_dir is not None:
        run_dir_name = args.run_dir

    input_file = args.input_file
    current_run = RunManager(datetime_string=run_dir_name, input_dsl_file=input_file)
    logger.info("\n".join(["", "=" * 70, "Running mlang transpiler", "=" * 70]))

    try:
        with open(Path(input_file), "r", encoding="utf-8") as f:
            source_text = f.read()
    except FileNotFoundError as fne:
        logger.error(f"Cannot continue: {fne}")

    current_run.copy_input_dsl_file()
    code_generator = sas_code_generator.SASCodeGenerator()
    program, symbols, output_code = compile_source(source_text, generator=code_generator, current_run=current_run)

    if args.debug: # print out the AST
        logger.debug("\n".join(["", "=" * 70, "Abstract Syntax Tree (debug)", "=" * 70]))
        for stmt in program.statements:
            logger.debug(pformat(stmt, width=100))

    if args.debug:
        logger.debug("\n".join(["", "="* 70,"Symbol Table (debug)", "="* 70]))
        for name, ds in symbols.datasets.items():
            logging.debug(f"Dataset: {name}")
            logging.debug(f"  source_path = {ds.source_path!r}")
            logging.debug(f"  tags        = {ds.tags}")
            for fname, fsym in ds.fields.items():
                logging.debug(f"  field {fname}: tags = {fsym.tags}")

    # Warnings detected?
    if len(symbols.warnings) != 0:
        logger.debug("\n".join(["", "="* 70,"Warnings", "="* 70]))
        for warn in symbols.warnings:
            logger.debug(f" - {warn}")
        current_run.write_warnings_file("warnings.log", symbols.warnings)

    # Errors detected?
    if len(symbols.errors) != 0:
        logger.error(f"{len(symbols.errors)} error(s) found during transpiler process. Please investigate these errors "
                     f"and adjust your mlang program.")
        current_run.write_error_file("errors.log", symbols.errors)
    else:
    # Happy path - write the output code and then exit the transpiler
        logger.debug("\n".join(["", "="* 70,"Output Code", "="* 70, output_code]))
        current_run.write_sas_file(output_code)

    logger.info("\n".join(["", "=" * 70, "Exiting transpiler.", "=" * 70]))

if __name__ == "__main__":
    main()
