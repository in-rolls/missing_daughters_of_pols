#!/bin/bash
# Guide for collecting data from all state assemblies
#
# This script provides commands for collecting data from each state
# using the election affidavit collector (most reliable source)

echo "=== Indian State Legislative Assembly Data Collection Guide ==="
echo ""
echo "Usage: Run individual commands for each state"
echo "The election affidavit data is most reliable as it's legally required"
echo ""

# Large states - Tier 1 Priority
echo "=== TIER 1: LARGE STATES ==="
echo "python collect_election_affidavits.py --state maharashtra --year 2019 --output ../../../data/"
echo "python collect_election_affidavits.py --state 'west bengal' --year 2021 --output ../../../data/"
echo "python collect_election_affidavits.py --state 'tamil nadu' --year 2021 --output ../../../data/"
echo "python collect_election_affidavits.py --state karnataka --year 2023 --output ../../../data/"
echo "python collect_election_affidavits.py --state gujarat --year 2022 --output ../../../data/"
echo "python collect_election_affidavits.py --state 'madhya pradesh' --year 2023 --output ../../../data/"
echo "python collect_election_affidavits.py --state rajasthan --year 2023 --output ../../../data/"
echo "python collect_election_affidavits.py --state bihar --year 2020 --output ../../../data/"
echo "python collect_election_affidavits.py --state 'andhra pradesh' --year 2019 --output ../../../data/"
echo "python collect_election_affidavits.py --state telangana --year 2023 --output ../../../data/"
echo ""

# Medium states - Tier 2
echo "=== TIER 2: MEDIUM STATES ==="
echo "python collect_election_affidavits.py --state odisha --year 2019 --output ../../../data/"
echo "python collect_election_affidavits.py --state kerala --year 2021 --output ../../../data/"
echo "python collect_election_affidavits.py --state punjab --year 2022 --output ../../../data/"
echo "python collect_election_affidavits.py --state haryana --year 2019 --output ../../../data/"
echo "python collect_election_affidavits.py --state jharkhand --year 2019 --output ../../../data/"
echo "python collect_election_affidavits.py --state assam --year 2021 --output ../../../data/"
echo "python collect_election_affidavits.py --state chhattisgarh --year 2023 --output ../../../data/"
echo "python collect_election_affidavits.py --state uttarakhand --year 2022 --output ../../../data/"
echo "python collect_election_affidavits.py --state 'himachal pradesh' --year 2022 --output ../../../data/"
echo ""

# Smaller states - Tier 3
echo "=== TIER 3: SMALLER STATES ==="
echo "python collect_election_affidavits.py --state goa --year 2022 --output ../../../data/"
echo "python collect_election_affidavits.py --state manipur --year 2022 --output ../../../data/"
echo "python collect_election_affidavits.py --state tripura --year 2023 --output ../../../data/"
echo "python collect_election_affidavits.py --state meghalaya --year 2023 --output ../../../data/"
echo "python collect_election_affidavits.py --state nagaland --year 2023 --output ../../../data/"
echo "python collect_election_affidavits.py --state mizoram --year 2023 --output ../../../data/"
echo "python collect_election_affidavits.py --state 'arunachal pradesh' --year 2019 --output ../../../data/"
echo "python collect_election_affidavits.py --state sikkim --year 2019 --output ../../../data/"
echo ""

echo "=== NOTES ==="
echo "1. These use MyNeta URLs which aggregate Election Commission affidavit data"
echo "2. Years shown are most recent elections; verify current status"
echo "3. Some states may have had elections more recently - update year accordingly"
echo "4. The script will create state-specific directories automatically"
echo "5. Progress is checkpointed so you can resume if interrupted"
