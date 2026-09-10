#================================================================================
#File        : transformer.py
#Author      : Eric C. Grasby, MSIQ
#Created     : 2026-07-31
#Dissertation: A Domain-Specific Language Approach to Monitoring and Surveillance in Wholesale Electricity Markets
#Institution : University of Arkansas at Little Rock
#Advisor     : Dr. Daniel Berleant
#--------------------------------------------------------------------------------
#Purpose     :
#    Handles organizing and writing output files from the transpiler
#
#Notes       :
#    This class establishes a clean "YYYYMMDD_HHMMSS" run directory per invocation of the transpiler
#
#Version     : 0.1.0
#Last Updated: 2026-08-20
#================================================================================

import datetime
import os
import shutil
from pathlib import Path
import logging
from typing import List

from files.symbol_table import SemanticError

logging = logging.getLogger(__name__)


class Run:

    def __init__(self, **kwargs):
        """
        Init object to track artifacts associated with a "run" of the transpiler program.
        """
        datetime_string = kwargs.get("datetime_string", None)
        if datetime_string is None:
           self.datetime_string = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        else:
            logging.info(f"User has requested to reprocess in an existing run directory ({datetime_string})")
            self.datetime_string = datetime_string
        self.input_dsl_file_full_path = kwargs.get("input_dsl_file")
        self.input_dsl_file= Path(self.input_dsl_file_full_path).name
        self.transpiler_base_path = Path(os.path.dirname(__file__))
        self.run_base_path = self.transpiler_base_path / "run"
        self.current_run_path = Path(self.run_base_path / self.datetime_string)

        if not os.path.isdir(self.run_base_path / self.datetime_string):
            self.current_run_path.mkdir(parents=True)
            logging.info(f"Created run directory.")

        logging.info(f"All output and log files will be written to: {self.current_run_path}")


    def copy_input_dsl_file(self) -> None:
        """
        Copy the input DSL file to the output run directory
        """
        # Copy the mlang input and store it alongside the "compiled" sas code
        shutil.copyfile(self.transpiler_base_path / self.input_dsl_file, self.current_run_path / self.input_dsl_file)


    def write_warnings_file(self, payload: List[SemanticError]) -> None:
        """
        Writes warnings to a warnings.log file
        """
        if len(payload) > 0:
            with open(Path(self.current_run_path,"warnings.log"), "w") as f:
                f.write("\n".join(warning.message for warning in payload))
                logging.info(f"Output warnings written to: warnings.log at {self.current_run_path}")

    def write_error_file(self, filename: str, payload: List[SemanticError]) -> None:
        """
        Writes data to a log file in the run directory present at self.current_run_path
        """
        if len(payload) > 0:
            with open(Path(self.current_run_path,filename), "w") as f:
                f.write("\n".join(error.message for error in payload))
                logging.info(f"Output log file written. If semantic errors were found during transpiler run"
                             f", please check the log at {self.current_run_path}")

    def write_sas_file(self, payload: str) -> None:
        """
        Writes data to a log file in the run directory present at self.current_run_path
        """
        if len(payload) > 0:
            with open(Path(self.current_run_path,f"{self.input_dsl_file[:-1]}.sas"), "w") as f:
                f.write(payload)
                logging.info(f"Output code written to: {self.current_run_path}")
