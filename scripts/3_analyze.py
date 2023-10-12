import os
import sys

# Add parent dir to path
sys.path.append("/".join(os.path.dirname(__file__).split("/")[0:-1]))

from typing import Tuple, Dict
import argparse
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
from scipy import stats
from tabulate import tabulate
from src.plot import plot_hline_chart
import src.utils as utils


def get_column(df: pd.DataFrame, provider: str, column: str) -> np.ndarray:
    data = df[df["image_provider"] == provider]
    return np.array(
        data.sort_values(by=["image_flavor"])[column])


def get_providers(df: pd.DataFrame, column: str) ->Tuple[np.ndarray,
                                                         np.ndarray,
                                                         np.ndarray]:
    org = get_column(df, "original", column)
    cg = get_column(df, "chainguard", column)
    rf = get_column(df, "rapidfort", column)
    return org, cg, rf

def _make_fig(ax: Axes, df: pd.DataFrame, column: str,
             title: str, xlabel: str):
    flavors = df["image_flavor"].unique()
    org, cg, rf = get_providers(df, column)
    plot_hline_chart(ax, org, cg, rf, flavors, title, xlabel)


def save_image_sz_fig(df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(8,6))
    _make_fig(ax, df, "image_size_mb",
              title="Image Size per Image",
              xlabel="Size (MB)")
    fig.tight_layout()
    fig.savefig(out_path)


def save_n_vulns_fig(df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(8,6))
    _make_fig(ax, df, "n_vulnerabilities",
              title="Number of Vulnerabilities per Image",
              xlabel="Num Vulnerabilities")
    fig.tight_layout()
    fig.savefig(out_path)


def save_n_comps_fig(df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(8,6))
    _make_fig(ax, df, "n_components",
              title="Number of Components per Image",
              xlabel="Num Components")
    fig.tight_layout()
    fig.savefig(out_path)


def paired_ttest(cg: np.ndarray, rf: np.ndarray) -> Tuple[float, float]:
    t_stat, p_val = stats.ttest_rel(cg, rf)
    return float(t_stat), float(p_val)


def summerize(data: np.ndarray) -> Dict[str, float]:
    return {
        "mean": float(np.mean(data)),
        "std": float(np.std(data)),
        "min": float(np.min(data)),
        "max": float(np.max(data))
    }


def _stats_summary(df: pd.DataFrame) -> Dict[str, any]:
    summary = {}
    for col in ["image_size_mb", "n_vulnerabilities", "n_components"]:
        _smry = {}
        org, cg, rf = get_providers(df, col)
        _smry["original"] = summerize(org)
        _smry["chainguard"] = summerize(cg)
        _smry["rapidfort"] = summerize(rf)
        
        t_stat, p_val = paired_ttest(cg, rf)
        _smry["t_stat"] = t_stat
        _smry["p_val"] = p_val

        summary[col] = _smry
    
    return summary


def save_stats_summary(df: pd.DataFrame, out_path: str):
    with open(out_path, "w") as fp:
        data = _stats_summary(df)
        json.dump(data, fp, indent=4)


def save_digests(df: pd.DataFrame, out_path: str):
    data = df[["image_provider", "image_flavor", "image_digest"]] \
           .sort_values("image_flavor")
    tab = tabulate(data, headers="keys", showindex=False)
    with open(out_path, "w") as fp:
        fp.write(tab)


def save_scanner_info(out_path: str):
    grype_v = utils.bash("grype --version").split(" ")[1]
    syft_v = utils.bash("syft --version").split(" ")[1]
    with open(out_path, "w") as fp:
        fp.write(tabulate([
            ["grype version", grype_v],
            ["syft version", syft_v]
        ], showindex=False))

def parse_args() -> Tuple[str, str]:
    parser = argparse.ArgumentParser(
                    prog='3_analyze.py',
                    description='Outputs figures and reports of analyzed data.')
    
    parser.add_argument("--dataset", "-d",
                        required=True,
                        help="Path of aggregated dataset (agg.csv).")
    
    parser.add_argument("--output-dir", "-o",
                        required=True,
                        help="The directory to save reports and figures.")

    ds_path = parser.parse_args().dataset
    out_dir = parser.parse_args().output_dir
    
    return ds_path, out_dir


def main():

    ds_path, out_dir = parse_args()

    df = pd.read_csv(ds_path)

    fig_path = os.path.join(out_dir, "figures")
    os.mkdir(fig_path)

    save_image_sz_fig(df, os.path.join(fig_path, "img_sz.png"))
    save_n_vulns_fig(df, os.path.join(fig_path, "n_vulns.png"))
    save_n_comps_fig(df, os.path.join(fig_path, "n_comps.png"))

    save_stats_summary(df, os.path.join(out_dir, "summary.json"))
    save_digests(df, os.path.join(out_dir, "digests.txt"))
    save_scanner_info(os.path.join(out_dir, "info.txt"))

if __name__ == "__main__":
    main()