"""
vulneribilities:
    image-name
    registry
    severity
    type

images:
    image-name
    registry
    image-size
    has-shell
    has-package-manager
"""

from typing import Dict, Tuple
import os
import json
import argparse
import pandas as pd


SIZES_CSV_FILENAME = "image_sizes.csv"
VULNS_CSV_FILENAME = "image_vulnerabilities.csv"


def parse_args() -> Tuple[str, str]:
    parser = argparse.ArgumentParser(
                    prog='parse.py',
                    description='Produces datasets from parsed scan reports.')
    
    parser.add_argument("--report-dir", "-r",
                        required=True,
                        help="The directory of scan reports.")
    parser.add_argument("--out-dir", "-o",
                        required=True,
                        help="The directory to save generated datasets.")

    report_dir = parser.parse_args().report_dir
    out_dir = parser.parse_args().out_dir
    
    return report_dir, out_dir


def add_row(row_data: Dict, df: pd.DataFrame) -> pd.DataFrame:
    new_row = pd.DataFrame(row_data, index=[0])
    return pd.concat([df, new_row], axis=0,
                     ignore_index=True)


def parse_image_name(filename: str) -> str:
    names = filename.split("-")
    if "chainguard" in names:
        return names[2]
    if "rapidfort" in names:
        if "official" in names:
            return "-".join(names[2:4])
        return names[2]
    if "alpine" in names:
        return names[-3]
    return names[-2]


def parse_registry_name(filename: str) -> str:
    names = filename.split("-")
    if "chainguard" in names:
        return "chainguard"
    if "rapidfort" in names:
        return "rapidfort"
    if "alpine" in names:
        return "alpine"
    return "other"


def parse_image_size(source: Dict) -> int:
    return source["target"]["imageSize"]


def parse_vulnerability(match: Dict) -> Dict:
    return {
        "severity": match["vulnerability"]["severity"].lower(),
        "type": match["artifact"]["type"].lower(),
        "language": match["artifact"]["language"].lower()
    }


def update_size_table(image_size: int,
                      image_name: str,
                      registry_name: str,
                      df: pd.DataFrame) -> pd.DataFrame:
    row_data = {
        "image-name": image_name,
        "registry-name": registry_name,
        "image-size": image_size}
    
    return add_row(row_data, df)


def update_vulnerabilities_table(vdata: Dict,
                                 image_name: str,
                                 registry_name: str,
                                 df: pd.DataFrame) -> pd.DataFrame:
    vdata.update({
        "image-name": image_name,
        "registry-name": registry_name
    })
    return add_row(vdata, df)


def process_reports(report_dir: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Define tables
    size_df = pd.DataFrame()
    vuln_df = pd.DataFrame()

    # Iterate over each report and parse contents
    for filename in os.listdir(report_dir):
        path = os.path.join(report_dir, filename)
        
        registry_name = parse_registry_name(filename)
        image_name = parse_image_name(filename)
        
        with open(path, "r") as fp:
            # Attempt to parse json
            try:
                data = json.load(fp)
            except json.decoder.JSONDecodeError:
                print(f"Error reading {filename}!!")
                continue

            # Update the image size table
            image_size = parse_image_size(data["source"])
            size_df = update_size_table(image_size,
                                        image_name,
                                        registry_name,
                                        size_df)

            # For each match, update the vulnerabilities table
            for match in data["matches"]:
                vdata = parse_vulnerability(match)
                vuln_df = update_vulnerabilities_table(vdata,
                                                       image_name,
                                                       registry_name,
                                                       vuln_df)
                
    return size_df, vuln_df
                

def main():
    report_dir, out_dir = parse_args()
    size_df, vuln_df = process_reports(report_dir)
    
    size_df.to_csv(os.path.join(out_dir, SIZES_CSV_FILENAME), 
                   index=False)
    vuln_df.to_csv(os.path.join(out_dir, VULNS_CSV_FILENAME),
                   index=False)


if __name__ == "__main__":
    main()