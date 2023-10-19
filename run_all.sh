#!/bin/bash

# Stage 1 - Perform Grype and Syft scans
rm -rf data
mkdir data
mkdir data/reports
python scripts/1_scan_images.py -i images.json -r data/reports

# Stage 2 - Build data sets from scan reports
mkdir data/data-sets
python scripts/2_build_datasets.py -r data/reports -o data/data-sets

# Stage 3 - Generate figures and summary statistics from data sets
mkdir data/analysis
python scripts/3_analyze.py -d data/data-sets/agg.csv -o data/analysis
