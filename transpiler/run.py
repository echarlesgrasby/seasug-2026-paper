"""
.. module:: Run
   :platform: Unix

   Establishes a clean "YYYYMMDD_HHMMSS" run directory per invocation of the transpiler
"""

import datetime
import os
from pathlib import Path
import logging

logging = logging.getLogger(__name__)
class Run:

    def __init__(self, datetime_string=None):
        self.run_base_path = Path(os.path.dirname(__file__)) / "run"
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


