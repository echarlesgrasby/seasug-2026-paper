# MLANG Todo List

## Priority

1. Develop code for writing tags (both data set level and field level)
2. Preprocessor code to identify fields in data files and compare to the fields that the user has written in the .mlang
file (user shouldn't be able to tag a field that doesn't exist on the data file)
3. Make sas-name-collision check at the field level
4. Make sas-name-collision after truncation check at the field level (done)
5. Setup logging throughout the transpiler application (done)
6. Data export to ".sas7bdat"
7. Need to add basic filters & joins so that the user can do some data transformation management 
(or at least allow them to submit queries that then get wrapped in PROC SQL;)
8. Need to add tag searching
9. Fix case insensitivity issue (transpiler is not considering "EIA_924_PLANTS" and "eia_924_plants" as the same
, even though they are)


## "Nice To Haves"

1. Print symbol table only when debug logging is requested
2. Print AST nodes only when debug logging is requested
3. Add support to create data sets in library other than WORK
4. Template preamble and postamble code so that it is not hardcoded in the code generator
5. Make a registry of all validation checks and integrate it into `validation.py`