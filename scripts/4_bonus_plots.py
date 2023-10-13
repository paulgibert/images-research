import pandas as pd
import matplotlib.pyplot as plt


def main():
    df = pd.read_csv("data/datasets/agg.csv")

    org = df[df["image_provider"] == "original"]
    cg = df[df["image_provider"] == "chainguard"]
    rf = df[df["image_provider"] == "rapidfort"]
    
    for prov, clr, lbl in zip([org, cg, rf],
                              ["#949494", "#3443f4", "#8dc7c7"],
                              ["Original", "Chainguard", "RapidFort"]):
        plt.scatter(prov["n_components"], prov["n_vulnerabilities"],
                    color=clr, label=lbl)
    
    plt.title("Number of Vulnerabilities vs Number of Components")
    plt.xlabel("Num Comp")
    plt.ylabel("Num Vuln")
    plt.legend(loc='upper right', ncols=1)

    plt.show()


if __name__ == "__main__":
    main()