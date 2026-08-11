
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
            

/* Create Dataset: EIA_SOURCE_PLANTS (invokes import_dataset__basic.sas) */
%import_dataset__basic(source=../data/EIA_924_PLANTS.csv,out_name=EIA_SOURCE_PLANTS,source_format=CSV);
        
PROC DATASETS library=WORK NOLIST;
    MODIFY EIA_SOURCE_PLANTS;
    XATTR SET DS SOURCE_ORG='Energy Information Authority (EIA)';
QUIT;
PROC DATASETS LIBRARY=WORK NOLIST;
    MODIFY EIA_SOURCE_PLANTS;
    XATTR ADD VAR UTILITY_ID (
                                    PRIMARY_KEY='True'
UNIQUE='True'
                                 );
QUIT;
PROC DATASETS LIBRARY=WORK NOLIST;
    MODIFY EIA_SOURCE_PLANTS;
    XATTR ADD VAR PLANT_CODE (
                                    PRIMARY_KEY='True'
                                 );
QUIT;

/* Create Dataset: EIA_SOURCE_UTILITIES (invokes import_dataset__basic.sas) */
%import_dataset__basic(source=../data/EIA_924_UTILITIES.csv,out_name=EIA_SOURCE_UTILITIES,source_format=CSV);
        
PROC DATASETS library=WORK NOLIST;
    MODIFY EIA_SOURCE_UTILITIES;
    XATTR SET DS SOURCE_ORG='Energy Information Authority (EIA)';
QUIT;
PROC DATASETS LIBRARY=WORK NOLIST;
    MODIFY EIA_SOURCE_UTILITIES;
    XATTR ADD VAR utility_id (
                                    primary_key='true'
unique='true'
                                 );
QUIT;