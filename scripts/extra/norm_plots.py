import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def main():
    df = pd.read_csv("data/datasets/agg.csv")
    df = df[["image_provider", "image_flavor", "image_size_mb"]] \
         .groupby(["image_provider", "image_flavor"]) \
         .first() \
         .reset_index()
    
    chainguard = df[df["image_provider"] == "chainguard"]
    rapidfort = df[df["image_provider"] == "rapidfort"]

    diff_df = chainguard.merge(rapidfort, how="left", on="image_flavor")
    diff = diff_df["image_size_mb_x"] - diff_df["image_size_mb_y"]
    
    plt.hist(diff, bins=15)
    plt.show()



if __name__ == "__main__":
    main()