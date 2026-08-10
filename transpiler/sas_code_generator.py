"""
SAS code generation

Eric C. Grasby
"""

from __future__ import annotations

from typing import List
from code_gen import CodeGenerator
from files.ast_nodes import CreateDatasetStmt, TagStmt, SearchStmt
from files.symbol_table import SymbolTable


class SASCodeGenerator(CodeGenerator):
    """
    Implements basic SAS code generation from the mlang source code
    """

    def preamble(self, symbols: SymbolTable) -> List[str]:
        return [

            """
/* Setup some global folder variables that we can reference throughout the SAS session */ 
%GLOBAL MAIN_FOLDER MACROS_FOLDER FCMP_FOLDER;

%LET MAIN_FOLDER=%SYSFUNC(PATHNAME(HOME))/sasuser.v94;
%LET MACROS_FOLDER=&MAIN_FOLDER./MACROS;
%LET FCMP_FOLDER=&MAIN_FOLDER./FCMP;

%PUT MAIN_FOLDER is: &MAIN_FOLDER.;

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
        return f"""
/* Create Dataset: {stmt.name} (invokes import_dataset__basic.sas) */
%import_dataset__basic(source={stmt.source.path},out_name={stmt.name},source_format={stmt.source.type});
        """

    def emit_tag(self, stmt: TagStmt, symbols: SymbolTable) -> str:
        pass

    def emit_search(self, stmt: SearchStmt, symbols: SymbolTable) -> str:
        pass

    def postamble(self, symbols: SymbolTable) -> List[str]:
        return []