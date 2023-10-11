import os
import sys

# Add parent dir to path
sys.path.append("/".join(os.path.dirname(__file__).split("/")[0:-1]))

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from src.plot import (plot_stacked_bar,
                      plot_grouped_bar,
                      plot_sbs_grouped_bar,
                      plot_hist,
                      plot_hline_chart)


def get_column(df: pd.DataFrame, provider: str, column: str) -> np.ndarray:
    data = df[df["image_provider"] == provider]
    return np.array(
        data.sort_values(by=["image_flavor"])[column])


def main():
    column = "n_vulnerabilities"

    df = pd.read_csv("data/datasets/agg.csv")
    flavors = df["image_flavor"].unique()

    cg = get_column(df, "chainguard", column)
    rf = get_column(df, "rapidfort", column)
    org = get_column(df, "original", column)

    """ Single plots """
    _, ax = plt.subplots()
    # plot_stacked_bar(ax, org, cg, rf, flavors)
    # plot_grouped_bar(ax, org, cg, rf, flavors, highlight_min=False)
    # plot_grouped_bar(ax, org, cg, rf, flavors, highlight_min=True)
    # plot_hist(ax, org, cg, rf, flavors,
    #           nbins=np.arange(0, np.max(org), 10),
    #           alpha=1,
    #           uselines=True)
    # plot_hline_chart(ax, org, cg, rf, flavors,
    #                  highlight_min=False)
    # plot_hline_chart(ax, org, cg, rf, flavors,
    #                  highlight_min=True)

    """ Double plots """
    _, ax = plt.subplots(1, 2)
    plot_sbs_grouped_bar(ax, org, cg, rf, flavors)
    plt.show()


if __name__ == "__main__":
    main()