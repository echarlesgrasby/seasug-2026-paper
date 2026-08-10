/* import_dataset__basic.sas */

%MACRO IMPORT_DATASET__BASIC(SOURCE=,LIBRARY=WORK,OUT_NAME=,SOURCE_FORMAT=);

    %LET SOURCE=%SYSFUNC(
                    TRANWRD(
                        %SYSFUNC(
                            TRANWRD(&SOURCE., %STR(%"),)
                    ), %STR(%'),)
                );
    %PUT Source file to be loaded is: &SOURCE.;
    %PUT The target library is: &LIBRARY.;

	%LET BASENAME=%SYSFUNC(SCAN(%SYSFUNC(SCAN(&SOURCE., -1, %STR(/))), 1, %STR(.)));
    %LET BASENAMEX=%SYSFUNC(SCAN(&SOURCE., -1, %STR(.)));

	%PUT Basename of target data set is: &BASENAME. and the file extension is: &BASENAMEX.;
    %PUT The incoming data will be loaded to &LIBRARY..&OUT_NAME.;

    PROC IMPORT DATAFILE="&SOURCE."
        OUT=&LIBRARY..&OUT_NAME.
        DBMS=&SOURCE_FORMAT.
        REPLACE;
        GETNAMES=YES;
        GUESSINGROWS=MAX;
    RUN;

%MEND IMPORT_DATASET__BASIC;
