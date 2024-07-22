"""
Stage 2 script.
Generates data sets from Grype and Syft scans.

Creates 4 data sets:

vulns.csv   -   A collection of every vulnerability per image across vendors
comps.csv   -   A collection of every component per image across vendors
sizes.csv   -   A collection of image sizes across vendors
agg.csv     -   Aggregated number of vulnerabilities, components, and image size per image across vendors.

Usage:
    python3 2_build_datasets.py -r [directory of scan reports] -o [directory to save data sets]

Example:
    python3 1_scan_images.py -r data/reports -o data/data-sets

Note: The reports directory is expected to be of the form
    
    reports/
        grype/
            - chainguard_nginx.json
            - rapidfort_nginx.json
            - baseline_nginx.json
            ...
        syft/
            - chainguard_nginx.json
            - rapidfort_nginx.json
            - baseline_nginx.json
            ...
"""


from typing import Tuple
import os
import sys
import argparse
import pandas as pd

# Add parent dir to path
sys.path.append("/".join(os.path.dirname(__file__).split("/")[0:-1]))

from src.report_parser import (
    ReportParserError,
    GrypeMetadataReportParser,
    GrypeReportParser,
    SyftReportParser)


BYTES_PER_MB = 1000000
SIZES_FILENAME = "sizes.csv"
VULNS_FILENAME = "vulns.csv"
COMPS_FILENAME = "comps.csv"
AGG_FILENAME = "agg.csv"


def build_ds(reports_dir: str, parser_type: type) -> pd.DataFrame:
    """
    Method for building data sets from Grype and Syft reports.

    @param reports_dir: The directory containing scan reports.
    @param parser_type: The type of parser to use
    @returns the pandas DataFrame returned by the parser
    """
    df = pd.DataFrame()

    # Loop over all files in the directory and apply parser
    for report_name in os.listdir(reports_dir):
        report_path = os.path.join(reports_dir, report_name)
        try:
            parser = parser_type(report_path)
        except ReportParserError:
            print(f"Failed to parse {report_path}!!")
            continue

        _df = parser.ds()

        # Concat report DataFrame to aggregate DataFrame of all reports
        df = pd.concat([df, _df],
                       axis=0, ignore_index=True)

    return df


def build_agg_ds(sizes_df: pd.DataFrame, vulns_df: pd.DataFrame,
                 comps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Method for building aggregate data set from Grype and Syft reports.
    Counts the number of vulnerabilities and components per image across vendors
    and creates the following columns:

        image_vendor                The image vendor. Ex chainguard
        image_type                  The image type. Ex nginx
        n_vulnerabilities           Number of vulnerabilities
        n_vulnerabilities_severe    Number of "high" and "critical" vulnerabilities
        n_components                Number of components
        image_size_bytes            Image size in bytes
        image_size_mb               Image size in MB
        vulns_per_comp              Vulnerabilities per component
        vulns_per_comp_severe       "high" and "critical" vulnerabilities per component

    @param sizes_df: The DataFrame from GrypeMetadataReportParser
    @param vulns_df: The DataFrame from GrypeReportParser
    @param comps_df: The DataFrame from SyftReportParser
    @returns an aggregated DataFrame of vulnerability and component data
    """
    keys = ["image_vendor", "image_type"]

    # Count vulnerabilities
    vuln_count_df = vulns_df.drop("severity", axis=1) \
                       .groupby(keys) \
                       .count() \
                       .reset_index() \
                       .rename(columns={"type": "n_vulnerabilities"})

    # Count severe vulnerabilities
    mask = (vulns_df["severity"] == "high") | (vulns_df["severity"] == "critical")
    sev_vuln_count_df = vulns_df[mask]
    sev_vuln_count_df = sev_vuln_count_df.drop("severity", axis=1) \
                                         .groupby(keys) \
                                         .count() \
                                         .reset_index() \
                                         .rename(columns={"type": "n_vulnerabilities_severe"})

    # Count components
    comps_df = comps_df.drop("type", axis=1) \
                       .groupby(keys) \
                       .count() \
                       .rename(columns={"name": "n_components"}) \
                       .reset_index()

    # Aggregate into one DataFrame
    agg_df = sizes_df.merge(vuln_count_df, how="outer",
                            on=keys) \
                     .merge(sev_vuln_count_df, how="outer",
                            on=keys) \
                     .merge(comps_df, how="outer",
                           on=keys) \
                     .fillna(0)

    agg_df["n_vulnerabilities"].astype("int")
    agg_df["image_size_mb"] = agg_df["image_size_bytes"] / BYTES_PER_MB
    agg_df["vulns_per_comp"] = agg_df["n_vulnerabilities"] / agg_df["n_components"]
    agg_df["severe_vulns_per_comp"] = agg_df["n_vulnerabilities_severe"] / agg_df["n_components"]

    return agg_df


def parse_args() -> Tuple[str, str]:
    """
    Parses script args.
    """
    parser = argparse.ArgumentParser(
                    prog=os.path.basename(__file__),
                    description='Builds datasets from grype and syft reports.')
    
    parser.add_argument("--reports-dir", "-r",
                        required=True,
                        help="The directory to save scan reports.")
    
    parser.add_argument("--output-dir", "-o",
                        required=True,
                        help="The directory to save generated datasets.")

    reports_dir = parser.parse_args().reports_dir
    out_dir = parser.parse_args().output_dir
    
    return reports_dir, out_dir


def main():
    """
    The main method of the script.
    Parses scan reports from Grpye and Syft, builds data sets,
    and saves the results to csv files.
    """
    print("STAGE 2: Building data sets")
    
    reports_dir, out_dir = parse_args()

    grype_reports_path = os.path.join(reports_dir, "grype")
    syft_reports_path = os.path.join(reports_dir, "syft")

    # Build data sets
    sizes_df = build_ds(grype_reports_path, GrypeMetadataReportParser)
    vulns_df = build_ds(grype_reports_path, GrypeReportParser)
    comps_df = build_ds(syft_reports_path, SyftReportParser)
    agg_df = build_agg_ds(sizes_df=sizes_df,
                          vulns_df=vulns_df,
                          comps_df=comps_df)

    # Save data sets
    sizes_df_path = os.path.join(out_dir, SIZES_FILENAME)
    sizes_df.to_csv(sizes_df_path, index=False)

    vulns_df_path = os.path.join(out_dir, VULNS_FILENAME)
    vulns_df.to_csv(vulns_df_path, index=False)

    comps_df_path = os.path.join(out_dir, COMPS_FILENAME)
    comps_df.to_csv(comps_df_path, index=False)

    agg_df_path = os.path.join(out_dir, AGG_FILENAME)
    agg_df.to_csv(agg_df_path, index=False)


if __name__ == "__main__":
    main()
