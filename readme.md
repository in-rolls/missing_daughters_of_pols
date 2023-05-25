### Missing Daughters of Indian Politicians

Indian politicians get a bad rap. They are thought to be corrupt, inept, and sexist. Here we check whether there is prima facie evidence for sex-selective abortion.

Using data from the Indian Government Website for the [Lok Sabha](https://sansad.in/ls), we find the following:

1. Sex Ratio across the 12--17th Lok Sabhas range from 104 to 114 (current LS).
2. Proportion daughters ranges from .45 ~ .47
3. No real diff. b/w BJP vs. rest

To put the numbers in context, we are looking at a shortfall of about 3--4%. Across ~1100 kids per session, it implies about 35+ missing daughters of the 500 or so MPs. Here's another way to look at the numbers from the 17th LS: If LS were a state, it would be the sixth worst (based on the sex ratio at birth established using [NFHS-5](https://en.wikipedia.org/wiki/List_of_states_and_union_territories_of_India_by_sex_ratio)). 


### Data

* [data](data/)

### Scripts

* [python notebook](https://github.com/in-rolls/missing_daughters_of_pols/blob/main/pol_daughters.ipynb)

### Key Results

| Lok Sabha| Proportion Daughters |
|---|---|
| 12 | 0.46 |
| 13 | 0.46 |
| 14 | 0.46 |
| 15 | 0.47 |
| 16 | 0.47 |
| 17 | 0.45 |

| Lok Sabha | numberOfSons | numberOfDaughters | sex_ratio |
|-----------|--------------|-------------------|---|
| 12        | 472.0        | 444.0 | 1.06 |
| 13 | 775.0 | 742.0 | 1.04 |
| 14 | 755.0 | 676.0 | 1.12 |
| 15 | 655.0 | 630.0 | 1.04 |
| 16 | 609.0 | 552.0 | 1.10 |
| 17 | 614.0 | 538.0 | 1.14 |

| partySname | numberOfSons | numberOfDaughters | sex_ratio |
|------------|--------------|-------------------|-----------|
| BJP        | 1591.0       | 1428.0            | 1.11 |
| INC        | 773.0        | 800.0             | 0.97 |
| CPI(M)     | 143.0        | 126.0             | 1.13  |
| SP         | 115.0        | 125.0             | 0.92  |
| BSP        | 110.0        | 79.0              | 1.39  |
| TDP        | 91.0         | 85.0              | 1.07  |
| SS         | 89.0         | 62.0              | 1.44  |
| JD(U)      | 86.0         | 64.0              | 1.34  |
| BJD        | 81.0         | 86.0              | 0.94  |
| AITC       | 78.0         | 60.0              | 1.30  |

