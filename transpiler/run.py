"""
.. module:: Run
   :platform: Unix

   Establishes a clean "YYYYMMDD_HHMMSS" run directory per invocation of the transpiler
"""

import datetime
import os
import shutil
from pathlib import Path
import logging
from typing import List

from files.symbol_table import SemanticError

logging = logging.getLogger(__name__)


class Run:

    def __init__(self, datetime_string=None):
        """
        Init object to track artifacts associated with a "run" of the transpiler program.
        """
        self.transpiler_base_path = Path(os.path.dirname(__file__))
        self.run_base_path = self.transpiler_base_path / "run"
        if datetime_string is None:
           self.datetime_string = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        else:
            logging.info(f"User has requested to reprocess in an existing run directory ({datetime_string})")
            self.datetime_string = datetime_string

        self.current_run_path = Path(self.run_base_path / self.datetime_string)

        if not os.path.isdir(self.run_base_path / self.datetime_string):
            self.current_run_path.mkdir(parents=True)
            logging.info(f"Created run directory.")

        logging.info(f"All output and log files will be written to: {self.current_run_path}")


    def copy_input_dsl_file(self, dsl_file_name="sample.mlang") -> None:
        """
        Copy the input DSL file to the output run directory
        """
        # Copy the mlang input and store it alongside the "compiled" sas code
        shutil.copyfile(self.transpiler_base_path / dsl_file_name, self.current_run_path / "sample.mlang")


    def write_error_file(self, filename: str, payload: List[SemanticError]) -> None:
        """
        Writes data to a log file in the run directory present at self.current_run_path
        """
        if len(payload) > 0:
            with open(Path(self.current_run_path,filename), "w") as f:
                f.write("\n".join(error.message for error in payload))
                logging.info(f"Output log file written. If semantic errors were found during transpiler run"
                             f", please check the log at {self.current_run_path}")

    def write_sas_file(self, filename: str, payload: str) -> None:
        """
        Writes data to a log file in the run directory present at self.current_run_path
        """
        if len(payload) > 0:
            with open(Path(self.current_run_path,filename), "w") as f:
                f.write(payload)
                logging.info(f"Output code written to: {self.current_run_path}")
