import os
import sys

# Add parent dir to path
sys.path.append("/".join(os.path.dirname(__file__).split("/")[0:-1]))

from typing import Tuple
import argparse
import pandas as pd
from src.report_parser import (
    ReportParserError,
    MetadataReportParser,
    GrypeReportParser,
    SyftReportParser
    )


METADATA_CSV = "sizes.csv"
VULNS_CSV = "vulns.csv"
COMPONENTS_CSV = "comps.csv"
AGG_CSV = "agg.csv"


def _build_ds(reports_path: str, parser_type: type) -> pd.DataFrame:
    df = pd.DataFrame()
    for file_name in os.listdir(reports_path):
        file_path = os.path.join(reports_path, file_name)
        try:
            parser = parser_type(file_path)
        except ReportParserError:
            print(f"Failed to parse {file_path}!")
            continue

        _df = parser.ds()

        df = pd.concat([df, _df],
                       axis=0, ignore_index=True)
    
    return df


def build_metadata_ds(reports_path: str) -> pd.DataFrame:
    return _build_ds(reports_path, MetadataReportParser)


def build_grype_ds(reports_path: str) -> pd.DataFrame:
    return _build_ds(reports_path, GrypeReportParser)


def build_syft_ds(reports_path: str) -> pd.DataFrame:
    return _build_ds(reports_path, SyftReportParser)


def agg_ds(meta_df: pd.DataFrame, grype_df: pd.DataFrame,
           syft_df: pd.DataFrame) -> pd.DataFrame:
    
    
    vulns_df = grype_df.drop("severity", axis=1) \
                       .groupby(["image_provider", "image_flavor"]) \
                       .count() \
                       .reset_index() \
                       .rename(columns={"type": "n_vulnerabilities"})

    grype_df_severe = grype_df[(grype_df["severity"] == "high") 
                               | (grype_df["severity"] == "critical")]
    vulns_df_severe = grype_df_severe.drop("severity", axis=1) \
                                     .groupby(["image_provider", "image_flavor"]) \
                                     .count() \
                                     .reset_index() \
                                     .rename(columns={"type": "n_vulnerabilities_severe"})
    
    comps_df = syft_df.drop("type", axis=1) \
                       .groupby(["image_provider", "image_flavor"]) \
                       .count() \
                       .rename(columns={"component_name": "n_components"}) \
                       .reset_index()
    
    agg_df = meta_df.merge(vulns_df, how="outer",
                           on=["image_provider", "image_flavor"]) \
                    .merge(vulns_df_severe, how="outer",
                           on=["image_provider", "image_flavor"]) \
                    .merge(comps_df, how="outer",
                           on=["image_provider", "image_flavor"]) \
                    .fillna(0)
    
    agg_df["n_vulnerabilities"].astype("int")
    agg_df["image_size_mb"] = agg_df["image_size_bytes"] / 1000000
    agg_df["vulns_per_comp"] = agg_df["n_vulnerabilities"] / agg_df["n_components"]

    return agg_df


def parse_args() -> Tuple[str, str]:
    parser = argparse.ArgumentParser(
                    prog='2_build_datasets.py',
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
    reports_dir, out_dir = parse_args()

    meta_df = build_metadata_ds(os.path.join(reports_dir, "grype"))
    meta_df.to_csv(os.path.join(out_dir, METADATA_CSV), index=False)

    grype_df = build_grype_ds(os.path.join(reports_dir, "grype"))
    grype_df.to_csv(os.path.join(out_dir, VULNS_CSV), index=False)

    syft_df = build_syft_ds(os.path.join(reports_dir, "syft"))
    syft_df.to_csv(os.path.join(out_dir, COMPONENTS_CSV), index=False)

    agg_df = agg_ds(meta_df, grype_df, syft_df)
    agg_df.to_csv(os.path.join(out_dir, AGG_CSV), index=False)


if __name__ == "__main__":
    main()