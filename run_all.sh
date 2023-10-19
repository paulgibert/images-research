#!/bin/bash

PARENT_DIR=data
DIR_NAME=$(date | cut -d " " -f 2-4 | sed 's\ \-\g')
DIR=$PARENT_DIR/$DIR_NAME

# Stage 1 - Perform Grype and Syft scans
rm -rf $DIR
mkdir $DIR
mkdir $DIR/reports
python scripts/1_scan_images.py -i images.json -r $DIR/reports

# Stage 2 - Build data sets from scan reports
mkdir $DIR/data-sets
python scripts/2_build_datasets.py -r $DIR/reports -o $DIR/data-sets

# Stage 3 - Generate figures and summary statistics from data sets
mkdir $DIR/analysis
python scripts/3_analyze.py -d $DIR/data-sets/agg.csv -o $DIR/analysis
