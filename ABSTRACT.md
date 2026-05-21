# ABSTRACT (no more than 1500 characters)

This paper presents a proof-of-concept design and implementation of a domain-specific language (DSL) for use in energy market monitoring. 
Energy markets are complex systems that enable market participants to economically trade energy at wholesale rates. 
Market monitors analyze these markets and screen for manipulative behavior, and often utilize SAS for data extraction, transformation, and analysis. 

While SAS is a powerful platform for working with data, not every market monitor is necessarily a trained programmer. 
DSLs enable non-programmers to solve problems without needing formal training in software development. 
The proposed framework of this paper extends the capabilities of SAS by implementing a custom grammar and parser, 
allowing a market monitoring analyst to write declarative surveillance logic statements in the provided DSL grammar. 
It then transpiles the high-level statements into legal SAS code, leveraging SAS data sets for data management and SAS procedures, 
DATA step programming, and SAS macros to handle complex functionality. 

This paper, additionally, demonstrates the flexibility of this proposed design by providing example scripts that satisfy several use-cases of this system. 
These use-cases were identified by an anonymous panel of market monitors as part of a Delphi study. 
