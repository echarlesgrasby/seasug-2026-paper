"""
Simple data "peek" utility.

This is loaded in by `validators.py`

"""

import pandas as pd

def peek_data_file(file_path: str, ds_name: str) -> pd.DataFrame:
    """
    Loads the first 10 records of a data file and inspects the header row to validate
    all field names. This can also be used to ensure that a field called out in
    an .mlang "program" exists in the source data
    """

    # should utilize standard delimiter ","
    data = pd.read_csv(file_path, dtype=str)
    return data.columns.to_list()


