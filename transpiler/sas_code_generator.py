#================================================================================
#File        : sas_code_generator.py
#Author      : Eric C. Grasby, MSIQ
#Created     : 2026-07-31
#Dissertation: A Domain-Specific Language Approach to Monitoring and Surveillance in Wholesale Electricity Markets
#Institution : University of Arkansas at Little Rock
#Advisor     : Dr. Daniel Berleant
#--------------------------------------------------------------------------------
#Purpose     :
#    An output code generator. The class receives the constructed SymbolTable and translates
#    those statements into valid SAS output code.
#
#Notes       :
#    This is a fairly basic program at the moment, but illustrates how the transpiler strategy can create SAS source code
#    from an mlang input program
#
#
#Version     : 0.1.0
#Last Updated: 2026-08-20
#================================================================================


from __future__ import annotations

from typing import List
from code_gen import CodeGenerator
from files.ast_nodes import CreateDatasetStmt, TagStmt, SearchStmt
from files.symbol_table import SymbolTable
from peek_data_file import load_sas_template_file

class SASCodeGenerator(CodeGenerator):
    """
    Implements basic SAS code generation from the mlang source code
    """

    def preamble(self, symbols: SymbolTable, **kwargs) -> List[str]:
        current_run=kwargs.get("current_run")

        return [

            f"""
/* Setup some global folder variables that we can reference throughout the SAS session */ 
%GLOBAL MAIN_FOLDER MACROS_FOLDER FCMP_FOLDER RUN_FOLDER OUTPUT_FOLDER;

%LET MAIN_FOLDER=%SYSFUNC(PATHNAME(HOME))/sasuser.v94;
%LET RUN_FOLDER=&MAIN_FOLDER./RUN;
%LET OUTPUT_FOLDER={current_run.datetime_string};
%LET MACROS_FOLDER=&MAIN_FOLDER./MACROS;
%LET FCMP_FOLDER=&MAIN_FOLDER./FCMP;

%PUT NOTE: MAIN FOLDER is: &MAIN_FOLDER.;
%PUT NOTE: RUN OUTPUT directory is &OUTPUT_FOLDER.;

/* Create a MACROS folder if user wishes to include custom macros */
data _null_;
    folder = dcreate("MACROS","&MAIN_FOLDER.");
    put "MACROS_FOLDER is &MACROS_FOLDER.";
run;

/* Create an FCMP folder if user wishes to create compiled functions */
data _null_;
    folder = dcreate("FCMP","&MAIN_FOLDER.");
    put "FCMP_FOLDER is &FCMP_FOLDER.";
run;

/* Create an RUN OUTPUT folder for where any data sets should be exported */
data _null_;
    folder = dcreate("RUN","&RUN_FOLDER.");
    folder = dcreate("&OUTPUT_FOLDER.", "&RUN_FOLDER.");
    put "NOTE: &OUTPUT_FOLDER." created within RUN folder. Any data set exports shall be created here.";
run;

/* Include all macros in the MACROS folder */
%macro run_macro_includes(folder);

	%let folder = %SYSFUNC(DEQUOTE(&folder.));
	%PUT folder is &folder.;

    %local filrf rc fid i filename memcnt;

    /* Assign a fileref to the directory */
    %let rc = %sysfunc(filename(filrf, &folder.));

    %if &rc. ne 0 %then %do;
        %put ERROR: Could not assign fileref to &folder.;
        %return;
    %end;

    /* Open the directory */
    %let fid = %sysfunc(dopen(&filrf.));

    %if &fid. eq 0 %then %do;
        %put ERROR: Could not open directory &folder.;
        %let rc = %sysfunc(filename(filrf));
        %return;
    %end;

    %let memcnt = %sysfunc(dnum(&fid.));

    %do i = 1 %to &memcnt.;
        %let filename = %qsysfunc(dread(&fid., &i.));

        /* skip including the file that we are running from... */
        %if %qupcase(&filename.) = SOME_FILE_THAT_YOU_WISH_TO_SKIP.SAS %THEN %GOTO continue;

        /* Only process files ending in .sas (case-insensitive) */
        %if %qupcase(%qscan(&filename., -1, .)) = SAS %then %do;
            %put NOTE: Including &folder./&filename.;
            %include "&folder./&filename.";
        %end;

       %continue:
    %end;

    /* Clean up */
    %let rc = %sysfunc(dclose(&fid.));
    %let rc = %sysfunc(filename(filrf));

%mend run_macro_includes;

/* Example call */
%run_macro_includes(&macros_folder.);
            """

        ]

    def emit_create_dataset(self, stmt: CreateDatasetStmt, symbols: SymbolTable) -> str:
        """
        Emit method for importing a data set into SAS
        """
        return f"""
/* Create Dataset: {stmt.name} (invokes import_dataset__basic.sas) */
%import_dataset__basic(source={stmt.source.path},out_name={stmt.name},source_format={stmt.source.type});
        """

    def emit_tag(self, stmt: TagStmt, symbols: SymbolTable) -> str:
        """
        Emit method for tagging a data set or individual field in SAS
        """
        if stmt.target.field_name is not None:
            tpl_file_name = "tag_field"
        else:
            tpl_file_name = "tag_data_set"
        tpl = load_sas_template_file(tpl_file_name)

        statement = (tpl
                     .replace("{{TARGET_LIBRARY}}", "WORK")
                     .replace("{{TARGET_DATASET}}",stmt.target.dataset_name)
                     .replace("{{FIELD_NAME}}", "" if stmt.target.field_name is None else stmt.target.field_name)
                     )

        tags_to_use = []
        for tag_pair in stmt.pairs:
            tags_to_use.append(f"{tag_pair.key}='{tag_pair.value}'")
        tags = "\n".join(tags_to_use)
        statement = statement.replace("{{TAG_PAIR}}",tags)
        return statement

    def emit_search(self, stmt: SearchStmt, symbols: SymbolTable) -> str:
        """
        Emit method for searching for a tagged data set or field in SAS
        """
        tpl = load_sas_template_file("search_tag")

        statement = (tpl
                     .replace("{{TAG_NAME}}",stmt.tag_name.upper())
                     .replace("{{ORDER_DIR}}", stmt.order.direction.upper()))

        return statement


    def postamble(self, symbols: SymbolTable) -> List[str]:
        """
        Emit method for writing postamble code to a SAS program
        """
        return []