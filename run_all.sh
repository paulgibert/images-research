#!/bin/bash

mkdir data
mkdir data/reports
python scripts/1_scan_images.py -r data/reports

mkdir data/datasets
python scripts/2_build_datasets.py -r data/reports -o data/datasets

mkdir data/analysis
python 3_analyze.py -d data/datasets/agg.csv -o data/analysis
