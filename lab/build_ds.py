from typing import Tuple
import os
import argparse
import pandas as pd
from report_parser import (
    ReportParserError,
    MetadataReportParser,
    GrypeReportParser,
    SyftReportParser
    )


METADATA_CSV = "metadata.csv"
VULNS_CSV = "vulns.csv"
COMPONENTS_CSV = "components.csv"


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


def parse_args() -> Tuple[str, str]:
    parser = argparse.ArgumentParser(
                    prog='build_ds.py',
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

    vuln_df = build_grype_ds(os.path.join(reports_dir, "grype"))
    vuln_df.to_csv(os.path.join(out_dir, VULNS_CSV), index=False)

    comps_df = build_metadata_ds(os.path.join(reports_dir, "syft"))
    comps_df.to_csv(os.path.join(out_dir, COMPONENTS_CSV), index=False)


if __name__ == "__main__":
    main()
