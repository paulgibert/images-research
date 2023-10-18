import os
import sys
from typing import Tuple, List
import argparse
from dataclasses import dataclass
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
from tabulate import tabulate

# Add parent dir to path
sys.path.append("/".join(os.path.dirname(__file__).split("/")[0:-1]))

from src.plot import MetricData, plot_hline_chart
from src import utils
from src.stats import MetricStats


@dataclass
class FigureParams:
    """
    A dataclass for figure parameters
    """
    column: str
    title: str
    xlabel: str
    filename: str


FIGSIZE = (8,6)
FIGURES = [
    FigureParams(
        column="image_sz_mb",
        title="MB per Image",
        xlabel="Size (MB)",
        filename="sizes_fig.png"
    ),
    FigureParams(
        column="n_vulnerabilities",
        title="Number of Vulnerabilities per Image",
        xlabel="Num Vulnerabilities",
        filename="vulns_fig.png"
    ),
    FigureParams(
        column="n_vulnerabilities_severe",
        title="Number of \"High\" and \"Critical\" Vulnerabilities per Image",
        xlabel="Num Vulnerabilities",
        filename="vulns_severe_fig.png"
    ),
    FigureParams(
        column="n_components",
        title="Number of Components per Image",
        xlabel="Num Vulnerabilities",
        filename="comps_fig.png"
    ),
    FigureParams(
        column="vulns_per_comp",
        title="Number of Vulnerabilites per Component per Image",
        xlabel="Vulnerabilites per Component",
        filename="vulns_p_comp_fig.png"
    ),
    FigureParams(
        column="vulns_per_comp_severe",
        title="Number of \"High\" and \"Critical\" Vulnerabilites per Component per Image",
        xlabel="Vulnerabilites per Component",
        filename="vulns_p_comp_severe_fig.png"
    )
]


def _get_column(agg_df: pd.DataFrame, vendor: str, column: str) -> Tuple[np.ndarray, List[str]]:
    """
    Get data of a vendor by column. The data should come from the aggregated
    data set build in the stage 2 script.

    @param agg_df: A pandas DataFrame containing the aggregate data
    @param vendor: The vendor to get data of
    @param column: The column to get data from
    @returns A Tuple of the vendor data and coresponding image types (data, types)
    """
    mask = agg_df["image_vendor"] == vendor
    by = "image_type"
    # Sort image_type in reverse alphabetical order
    # (This will plot in alphabetical order)
    data = agg_df[mask].sort_values(by=by, ascending=False)
    types = list(data["image_type"])
    return np.array(data[column]), types


def _get_data(agg_df: pd.DataFrame, column: str) -> MetricData:
    """
    Get a MetricData object containing data for all vendors
    of a specefic column.

    @param agg_df: A pandas DataFrame containing the aggregate data
    @param column: The column to get data from
    @returns: A MetricData object of the provided column
    """
    baseline, baseline_types = _get_column(agg_df, "original", column)
    rapidfort, rapidfort_types = _get_column(agg_df, "rapidfort", column)
    chainguard, chainguard_types = _get_column(agg_df, "chainguard", column)

    # Sanity check to ensure all data is aligned
    utils.check_equal_contents([baseline_types,
                                rapidfort_types,
                                chainguard_types])

    return MetricData(baseline=baseline,
                      rapidfort=rapidfort,
                      chainguard=chainguard,
                      image_types=baseline_types)


def _build_figure(ax: Axes, agg_df: pd.DataFrame, params: FigureParams):
    """
    A helper function for building figures.

    @param ax: The matplotlib axis to plot on
    @param agg_df: A pandas DataFrame containing the aggregate data
    @param params: A FigureParams object describing the figure
    """
    data = _get_data(agg_df, params.column)
    plot_hline_chart(ax=ax,
                     data=data,
                     title=params.title,
                     xlabel=params.xlabel)


def build_and_save_figures(agg_df: pd.DataFrame, out_dir: str):
    """
    Builds and saves all the of the figures in the study.

    @param agg_df: A pandas DataFrame containing the aggregate data
    @param out_dir: The directory to save all figures
    """
    for params in FIGURES:
        fig, ax = plt.subplots(figsize=FIGSIZE)
        _build_figure(ax, agg_df, params)
        fig.tight_layout()
        out_path = os.path.join(out_dir, params.filename)
        fig.savefig(out_path)


def calculate_and_save_stats(agg_df: pd.DataFrame, out_path: str):
    """
    Calculates summary statistics for each vendor across all columns.

    @param agg_df: A pandas DataFrame containing the aggregate data
    @param out_path: The path to save the summary
    """
    table = [[
        "Figure Title",
        "Column",
        "Baseline Mean",
        "Chainguard Mean",
        "Chainguard % Reduction",
        "Chainguard < RapidFort Pval",
        "RapidFort Mean",
        "RapidFort % Reduction",
        "RapidFort < Chainguard Pval"]]

    for params in FIGURES:
        data = _get_data(agg_df, params.column)
        stats = MetricStats(data)
        # Metadata
        row = [params.title, params.column]
        # Baseline stats
        row.append(np.mean(data.baseline))
        # Chainguard stats
        row.append(np.mean(data.chainguard))
        row.append(stats.chainguard_reduction())
        row.append(stats.test_chainguard_lt_rapidfort()[1])
        # RapidFort stats
        row.append(np.mean(data.rapidfort))
        row.append(stats.rapidfort_reduction())
        row.append(stats.test_rapidfort_lt_chainguard()[1])

        table.append(row)
    
    with open(out_path, "r", encoding="utf-8") as fp:
        fp.write(tabulate(table, headers="firstrow"))


def parse_args() -> Tuple[str, str]:
    """
    Parses script args.
    """
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
    """
    The main method of the script.
    Builds figures and summary statistics
    from aggregate data set.
    """
    ds_path, out_dir = parse_args()

    # Read aggregate data set
    agg_df = pd.read_csv(ds_path)

    # Build and save all figures
    fig_dir = os.path.join(out_dir, "figures")
    utils.mkdir(fig_dir)
    build_and_save_figures(agg_df, fig_dir)

    # Calculate and save stats
    stats_path = os.path.join(out_dir, "summary.txt")
    calculate_and_save_stats(agg_df, stats_path)


if __name__ == "__main__":
    main()