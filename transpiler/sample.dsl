/* load and label generating plants from the EIA */
CREATE DATASET EIA_SOURCE_PLANTS FROM CSV("../../data/EIA_924_PLANTS.csv");

TAG EIA_SOURCE_PLANTS WITH SOURCE_ORG = "Energy Information Authority (EIA)";

TAG EIA_SOURCE_PLANTS.UTILITY_ID
WITH (PRIMARY_KEY = "True"
, UNIQUE = "True"
, );

TAG EIA_SOURCE_PLANTS.PLANT_CODE WITH PRIMARY_KEY = "True";

/* load and label electric utilities from the EIA */
CREATE DATASET EIA_SOURCE_UTILITIES FROM CSV("../../data/EIA_924_UTILITIES.csv");

TAG EIA_SOURCE_UTILITIES WITH SOURCE_ORG = "Energy Information Authority (EIA)";

tag eia_source_utilities.utility_id with (primary_key = "true", unique = "true");

SEARCH BY TAG(PRIMARY_KEY) THEN ORDER BY ASC;
