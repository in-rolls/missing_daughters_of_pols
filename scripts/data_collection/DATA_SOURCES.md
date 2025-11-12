# Comprehensive Data Sources for Missing Daughters Research

This document lists all potential data sources for expanding the research on sex ratios among children of Indian politicians.

## Current Coverage

### ✅ National Parliament
- **Lok Sabha** (12th-17th): Complete ✓
- **Rajya Sabha**: Collected, needs analysis

### ✅ State Assemblies
- **Delhi**: Complete ✓
- **Uttar Pradesh**: PDFs collected, needs extraction

### 🎯 To Be Collected
- 26 other state assemblies (see priority list below)

## Data Source Categories

### 1. State Legislative Assemblies (TOP PRIORITY)

**Why Priority:**
- Large sample size (4,000+ MLAs across all states)
- Comparable to Lok Sabha members in power/status
- State-level variation can reveal regional patterns

**Data Sources:**
1. **MyNeta/ADR (myneta.info)** - ⭐ MOST RELIABLE
   - Affidavit data is legally required
   - Includes family information
   - Searchable by state and year
   - Coverage: All states, recent elections

2. **State Assembly Websites** (state-specific)
   - Official biographical data
   - Quality varies significantly
   - May require web scraping

3. **Election Commission of India** (eci.gov.in)
   - Official source for affidavits
   - Bulk downloads available
   - Technical access may be challenging

**Expected Yield:** ~3,000-4,000 MLAs with complete data

### 2. Historical State Assembly Data

**Why Important:**
- Track changes over time
- Compare with historical Lok Sabha trends
- Control for cohort effects

**Data Sources:**
- Previous assembly sessions (e.g., 15th, 16th, 17th)
- May be harder to access than current data
- Archive.org may have cached versions

**Expected Yield:** Additional ~5,000-10,000 records

### 3. Municipal Governments

**Why Important:**
- Test if the pattern extends to local government
- Different socioeconomic profile than state/national politicians
- Large sample size

**Data Sources:**

#### Major Metropolitan Cities
1. **Mumbai Municipal Corporation** (288 corporators)
2. **Delhi Municipal Corporation** (272 councillors)
3. **Bangalore/BBMP** (198 corporators)
4. **Chennai Corporation** (200 councillors)
5. **Kolkata Municipal Corporation** (144 councillors)
6. **Hyderabad/GHMC** (150 corporators)

#### Other Major Cities
- Pune, Ahmedabad, Surat, Jaipur, Lucknow, Kanpur
- Total: ~30-40 major cities

**Challenges:**
- Each city has different data format
- Information may not be online
- May need RTI (Right to Information) requests

**Expected Yield:** ~3,000-5,000 municipal representatives

### 4. National-Level Positions

#### Union Cabinet Ministers
- **Current and Historical Cabinet Members**
- Data sources: PMO website, Ministry websites
- Sample size: ~300-500 across multiple governments

#### Chief Ministers
- **All States, Historical Data**
- High-profile individuals
- Data often available in biographical sources
- Sample size: ~200-300 individuals

#### Governors
- **Current and Past Governors**
- Appointed positions, different profile
- Sample size: ~100-150

### 5. Panchayati Raj (Rural Local Government)

**Why Important:**
- Much larger sample size (millions of elected representatives)
- Different socioeconomic background
- Could show if pattern is universal or elite-specific

**Data Sources:**
- Ministry of Panchayati Raj
- State Rural Development departments
- Very difficult to aggregate nationally

**Challenges:**
- Data not centralized
- Quality and availability vary widely
- May require state-by-state collection

**Expected Yield:** Potentially huge (100,000+), but very difficult

### 6. Political Dynasties Database

**Why Important:**
- Control for family political background
- May show stronger/weaker effects for political families

**Data Sources:**
- No central database exists
- Would need to be constructed manually
- Academic research papers may have partial data

**Resources:**
- Patrick French's work on dynasties
- Media investigations
- Wikipedia lists of political families

### 7. Comparative Data: Other Elites

To contextualize findings, compare with other elite groups:

#### Judiciary
- **High Court and Supreme Court Judges**
- Public biographical data often available
- Sample size: ~1,000 judges

#### Bureaucracy (IAS/IPS Officers)
- **Senior civil servants**
- Data availability: Limited
- May need RTI requests

#### Business Leaders
- **Forbes India Rich List**
- **Corporate Board Members**
- Often have public biographical data
- Sample size: ~500-1,000

#### Academic/Medical Professionals
- **University Professors**
- **Senior Doctors**
- Control group from different elite background

## Data Quality Assessment

### High Quality (Reliable, Structured)
1. ✅ Election Commission affidavits (via MyNeta)
2. ✅ Official parliamentary websites (Lok/Rajya Sabha)
3. ✅ Government gazettes

### Medium Quality (Available but Inconsistent)
1. ⚠️ State assembly websites
2. ⚠️ Municipal corporation websites
3. ⚠️ Media biographical databases

### Low Quality (Difficult to Access/Aggregate)
1. ❌ Panchayati Raj data
2. ❌ Historical archives
3. ❌ RTI-dependent sources

## Recommended Collection Priority

### Phase 1: Quick Wins (1-2 months)
1. ✅ Complete all state assemblies via MyNeta (most recent elections)
2. ✅ Extract UP data from existing PDFs
3. ✅ Analyze Rajya Sabha collected data

**Impact:** ~3x sample size, state-level analysis possible

### Phase 2: Expand Coverage (2-3 months)
1. Historical state assembly data (1-2 previous sessions)
2. Top 10 municipal corporations
3. National-level positions (Cabinet, CMs, Governors)

**Impact:** ~5-6x sample size, temporal trends, different government levels

### Phase 3: Comprehensive (3-6 months)
1. All major municipal corporations (~40 cities)
2. Comparative elite groups (judiciary, business)
3. Political dynasties analysis

**Impact:** Comprehensive picture, comparative context

### Phase 4: Deep Research (6+ months)
1. Panchayati Raj representatives (selected states)
2. Historical data mining (pre-2000)
3. Qualitative case studies

## Data Collection Feasibility Matrix

| Source | Sample Size | Data Availability | Collection Difficulty | Priority |
|--------|-------------|-------------------|----------------------|----------|
| State Assemblies (current) | ~4,000 | High | Low | ⭐⭐⭐⭐⭐ |
| State Assemblies (historical) | ~10,000 | Medium | Medium | ⭐⭐⭐⭐ |
| Rajya Sabha analysis | ~2,000 | High | Low | ⭐⭐⭐⭐⭐ |
| Municipal (major cities) | ~3,000 | Medium | Medium | ⭐⭐⭐ |
| Municipal (all) | ~10,000 | Low | High | ⭐⭐ |
| Union Cabinet | ~500 | High | Low | ⭐⭐⭐ |
| Chief Ministers | ~300 | High | Low | ⭐⭐⭐ |
| Judiciary | ~1,000 | Medium | Medium | ⭐⭐⭐ |
| Business Leaders | ~1,000 | Medium | Medium | ⭐⭐ |
| Panchayati Raj | ~100,000+ | Very Low | Very High | ⭐ |

## Technical Considerations

### Rate Limiting
- Respect website rate limits (1-2 seconds between requests)
- Use checkpointing to allow resumption
- Monitor for IP blocking

### Data Storage
- Store raw data (JSON/HTML) separately from processed data
- Keep data provenance (source URL, collection date)
- Version control for data processing scripts

### Legal/Ethical
- All data should be from public sources
- Respect privacy considerations
- Election affidavits are public documents (legal to use)
- Be careful with children's names (can anonymize)

### Data Quality
- Validate against multiple sources when possible
- Flag uncertain/incomplete records
- Document data limitations clearly

## Resources

### Key Websites
- MyNeta: https://myneta.info
- Sansad.in: https://sansad.in
- Election Commission: https://eci.gov.in
- State Assembly portals (varies by state)

### Academic References
- Studies on political dynasties in India
- Research on sex-selective abortion
- Demographic data from NFHS surveys

### Technical Tools
- Python libraries: requests, BeautifulSoup, pandas, pdfplumber
- Data validation tools
- Statistical analysis: R or Python

## Next Steps

1. ✅ Use existing scripts to collect all state assemblies
2. ✅ Expand dataset to ~10,000-15,000 politicians
3. ✅ Analyze patterns by state, party, and time period
4. ✅ Compare with general population trends
5. ✅ Publish extended findings
