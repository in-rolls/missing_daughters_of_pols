### Missing Daughters of Indian Politicians

In 1992, when Amartya Sen first raised the issue of missing women, India had a shortfall of 37 million women. One reason women are missing is that tens of millions of Indians choose to abort their would-be daughters. In 2010, the sex ratio at birth---the ratio of sons to daughters---was 111. To put this into context, the natural sex ratio is about 105. A move from 105 to 111 means that for every 100 children who are born, parents choose to abort 6 daughters. In 2011, about 20 million kids were born in India. And about 1.2 million would-be daughters were aborted. Sex-selective abortions are but one part of the story. About half of the missing women go missing in adulthood, because of malnutrition, violence, worse healthcare, etc. ([Anderson and Ray, 2010 (pdf)](https://pages.nyu.edu/debraj/Papers/AndersonRay.pdf)). In the last decade, however, we have made some progress, with the sex ratio at birth declining to 108 in 2021 ([Pew](https://www.pewresearch.org/religion/2022/08/23/indias-sex-ratio-at-birth-begins-to-normalize/)).

Against this backdrop, I examine whether India's political elites have missing daughters. Using official biographical data on Lok Sabha members from https://sansad.in/ls, I estimate the number of missing daughters among India's political elites. Aggregating across the 12--17 Lok Sabhas spanning 1998--2023, the aggregate sex ratio of children is 108.5. To put the number in context, we are looking at a shortfall of about 3--4 daughters. Across ~4500 kids, it implies about 135+ missing daughters of the 1,785 unique MPs. The average proportion of female children is .46 (when the expectation is ~.49). Both numbers are highly statistically unlikely to occur due to chance. 

While the aggregate numbers are bad enough, the sex ratio and the proportion of female children for the 17th Lok Sabha are eye-catchingly bleak at 114 and .44 respectively (see Tables 2 and 3). Here's another way to look at the numbers from the 17th LS: If LS were a state, it would be the sixth worst (based on the sex ratio at birth established using [NFHS-5](https://en.wikipedia.org/wiki/List_of_states_and_union_territories_of_India_by_sex_ratio)).

There is a positive (but weak) correlation (~ .14) between the number of kids and the proportion of female children, suggesting male stopping rules (see [here](https://github.com/soodoku/prop_male)). There is some evidence that the sex ratio is more skewed among BJP legislators than others though we cannot be confident that it isn't because of chance alone (see Table 4 but also the [notebook](https://github.com/in-rolls/missing_daughters_of_pols/blob/main/pol_daughters.ipynb) for analyses on proportion daughters by party, etc.) Lastly, Table 5 shows that sex ratio is more skewed among legislators with smaller families.


### Data

* [data](data/)

### Scripts

* [python notebook](https://github.com/in-rolls/missing_daughters_of_pols/blob/main/pol_daughters.ipynb)

### Key Results

Table 1: Average Number of Children by LS Session


| Lok Sabha | Mean Number of Children    |
|--------|----------|
| 12     | 2.82 |
| 13     | 2.82 |
| 14     | 2.66 |
| 15     | 2.49 |
| 16     | 2.20 |
| 17     | 2.04 |


Table 2: Average Proportion Daughters by LS Session

Lok Sabha | Proportion Daughters
-------|-------
12 | .46
13 | .49
14 | .45
15 | .46
16 | .48
17 | .44

Table 3: Sex Ratio by LS Session

|   Lok Sabha |   Number of Sons |   Number of Daughters |   sex ratio |
|-----:|---------------:|--------------------:|------------:|
|   12 |            472 |                 444 |    1.06  |
|   13 |            775 |                 742 |    1.04  |
|   14 |            755 |                 676 |    1.12  |
|   15 |            655 |                 630 |    1.04  |
|   16 |            609 |                 552 |    1.10  |
|   17 |            614 |                 538 |    1.14  |

Table 4: Party-wise Sex Ratio for Cases Where We Have Enough Data

| Party   |   Number of Sons |   Number of Daughters |   sex ratio |
|:-------------|---------------:|--------------------:|------------:|
| BSP          |            103 |                  71 |    1.45   |
| BJP          |            858 |                 751 |    1.14  |
| CPI(M)       |             74 |                  67 |    1.10  |
| SP           |             80 |                  75 |    1.07 |
| TDP          |             64 |                  61 |    1.05 |
| INC          |            470 |                 493 |    0.95 |
| DMK          |             49 |                  52 |    0.94 |
| AIADMK       |             57 |                  61 |    0.93 |
| BJD          |             45 |                  54 |    0.83 |


Table 5: Sex Ratio by Number of Children


| Number of Kids | Proportion of Daughters  | N |
|----------|-----------|----------|
| 1     | .46  | 194      |
| 2      | .42  | 672      |
| 3      | .47  | 380      |
| 4      | .52  | 200      |
| 5      | .55  | 104      |
| 6      | .57  | 33       |

