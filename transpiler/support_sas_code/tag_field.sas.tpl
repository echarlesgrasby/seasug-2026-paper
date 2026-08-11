PROC DATASETS LIBRARY={{TARGET_LIBRARY}} NOLIST;
    MODIFY {{TARGET_DATASET}};
    XATTR ADD VAR {{FIELD_NAME}} (
                                    {{TAG_PAIR}}
                                 );
QUIT;
