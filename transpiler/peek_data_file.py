#================================================================================
#File        : peek_data_file.py
#Author      : Eric C. Grasby, MSIQ
#Created     : 2026-07-31
#Dissertation: A Domain-Specific Language Approach to Monitoring and Surveillance in Wholesale Electricity Markets
#Institution : University of Arkansas at Little Rock
#Advisor     : Dr. Daniel Berleant
#--------------------------------------------------------------------------------
#Purpose     :
#    Allows the transpiler to "peek" data files that are different than .mlang files. This allows us to
#    inspect field names on data files and load in template (.tpl) files that contain snippets of output SAS code.
#Notes       :
#    TODO: This is a catch-all and may be renamed to a general utility function lib at some point
#
#
#Version     : 0.1.0
#Last Updated: 2026-08-24
#================================================================================

import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def peek_data_file(file_path: str, ds_name: str) -> pd.DataFrame:
    """
    Loads the header record of a data file and inspects the header row to validate
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
    file_path = Path("support_sas_code")
    template_files = {
        "tag_data_set": "tag_data_set.sas.tpl",
        "tag_field": "tag_field.sas.tpl",
        "search_tag": "search_tags.sas.tpl"
    }

    try:
        tpl_file_name = template_files[template_name]
    except KeyError:
        msg = f"{template_name} not yet implemented and does not exist in template_files"
        logging.error(msg)
        raise KeyError(msg)

    file_path = file_path / tpl_file_name
    lines = []
    with open(file_path, "r") as f:
        for line in f.readlines():
            lines.append(line.replace("\n", ""))
        return "\n".join(lines)

