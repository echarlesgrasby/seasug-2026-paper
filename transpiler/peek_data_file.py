"""
Simple data "peek" utility.

This is loaded in by `validators.py`

"""

import pandas as pd
from pathlib import Path

def peek_data_file(file_path: str, ds_name: str) -> pd.DataFrame:
    """
    Loads the first 10 records of a data file and inspects the header row to validate
    all field names. This can also be used to ensure that a field called out in
    an .mlang "program" exists in the source data
    """

    # should utilize standard delimiter ","
    data = pd.read_csv(file_path, dtype=str)
    return data.columns.to_list()

def load_sas_template_file(template_name: str) -> str:
    """
    Loads a .tpl file that has SAS code w/ placeholders. Caller is responsible for injecting values
    to replace placeholders.
    """
    file_path = Path()

    if template_name == "tag_data_set":
        file_path = Path("support_sas_code", "tag_dataset.sas.tpl")
    elif template_name == "tag_field":
        file_path = Path("support_sas_code", "tag_field.sas.tpl")
    else:
        raise NotImplementedError(f"{template_name} not yet implemented")

    lines = []

    with open(file_path, "r") as f:
        for line in f.readlines():
            lines.append(line.replace("\n", ""))
        return "\n".join(lines)

