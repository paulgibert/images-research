#!/bin/bash

mkdir data
mkdir data/scans
python scripts/1_scan_images.py -r data/scans

mkdir data/datasets
python scripts/2_build_datasets.py -r data/scans -o data/datasets

mkdir data/analysis
python scripts/3_analyze.py -d data/datasets/agg.csv -o data/analysis
