# seasug-2026-paper
Repository for [SEASUG 2026 Paper](https://sesug.org/SEASUG2026/index.php "Southeast Atlantic SAS Users Group") (co-authored with Dr. Daniel Berleant and Dr. Maria Gingras)

**A Domain-Specific Computer Language for Market Monitoring: From Domain Logic to SAS Code**

**Keywords**: domain-specific language, analyst abstraction, energy market, market monitoring, transpiler

> [!NOTE]
> There are some sections of this paper that are referenced from the first author's (Eric C. Grasby) dissertation.
> This dissertation is still a draft (has not been published with ProQuest) at the time of writing this paper.

## Abstract

This paper presents a proof-of-concept design of a domain-specific language (DSL) for use in wholesale electric market monitoring and applies the DSL to an industry use case. 
Wholesale electric markets competitively dispatch power plants, while respecting the constraints of the electric grid, to minimize the cost of electricity production. 
Market monitors are charged with analyzing data from these markets to screen for prohibited behavior among market participants to protect consumers 
from unduly high prices and to maintain the reliability of the electric grid.

To fulfill their duties, market monitors must extract, transform, and analyze data from multiple sources, often without sophisticated programming skills. 
Additionally, electric market data is complex and often fragmented, leading to issues that transcend simple programming problems. 
Together, these issues create a barrier for market monitors to efficiently and accurately complete their duties. 
This paper presents one viable solution to both problems: 
a DSL that allows a market monitor to declare the metrics that they wish to analyze 
and a transpiler that translates their input into valid code. 
This DSL leverages SAS® data sets for data management and SAS procedures, DATA step programming, and SAS macros to perform transformations.

Finally, this paper illustrates this proposed design by demonstrating how a user can generate SAS code to fulfill
common and critical market monitoring tasks.

## Author Biographies

### Eric Grasby

Eric Charles Grasby is an experienced programmer analyst with professional experience spanning the database marketing and electric regional transmission organization (RTO) sectors. 
He holds a Bachelor’s degree in Information Science and a Master of Science in Information Quality from the University of Arkansas at Little Rock, where he is currently pursuing a Ph.D. in Computer and Information Science. 
His research interests focus on the intersection of language engineering and information quality. Since 2020, he has worked at SPP (Southwest Power Pool), most recently as a market monitor since 2023.

### Dr. Daniel Berleant

Daniel Berleant (PhD '91, UT Austin) is currently a faculty member at the University of Arkansas at Little Rock, where he has been since 2006. He has advised 22 PhD students, over 60 master's students, and published well over 100 articles. He also wrote a book on the future which helps bring the excitement of science and engineering concepts to a lay audience.

### Dr. Maria Gingras

Dr. Maria Gingras (PhD 2017, Ecology; Environment Science and Policy, UC Davis) is an experienced economist and electric market analyst. She has worked in several disciplines in the wholesale electric market space, including a position as an analyst in the Federal Energy Regulatory Commission (FERC) Office of Enforcement.

## "License"

Please cite with proper credit to the authors.

__IEEE Format__

E. Grasby, D. Berleant, and M. Gingras, “A Domain-Specific Computer Language for Market Monitoring: From Domain Logic to SAS Code,” in SEASUG 2026 Proceedings, Oct. 2026. [Online]. Available: [https://github.com/echarlesgrasby/seasug-2026-paper/blob/master/SEASUG_42-2026_Grasby_Berleant_Gingras.pdf](https://github.com/echarlesgrasby/seasug-2026-paper/blob/master/SEASUG_42-2026_Grasby_Berleant_Gingras.pdf)

__BibTex Format__

```
@inproceedings{grasby2026domain,
  author    = {E. Grasby and D. Berleant and M. Gingras},
  title     = {A Domain-Specific Computer Language for Market Monitoring: From Domain Logic to SAS Code},
  booktitle = {SEASUG 2026 Proceedings},
  month     = oct,
  year      = {2026},
  url       = {https://github.com/echarlesgrasby/seasug-2026-paper/blob/master/SEASUG_42-2026_Grasby_Berleant_Gingras.pdf},
  note      = {Online}
}
```
