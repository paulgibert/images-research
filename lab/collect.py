from typing import Dict
import os
import json
import pandas as pd


IMAGES_PATH = "images.json"
TMP_DIR = "tmp"
REPORT_PATH = os.path.join(TMP_DIR, "report.json")
DATA_OUT_PATH = "results.csv"
SEVERITIES = ["critical", "high", "medium", "low", "negligible", "unknown"]


def pull_image(image: str):
    cmd = f"docker pull {image}"
    os.system(cmd)


def scan_image(image: str, out_path: str):
    cmd = f"grype {image} -o json > {out_path}"
    os.system(cmd)


def rm_image(image: str):
    cmd = f"docker image rm {image}"
    os.system(cmd)


def read_report_num_vulns(report: Dict) -> Dict:
    vulns = {k: 0 for k in SEVERITIES}
    for match in report["matches"]:
        severity = match["vulnerability"]["severity"].lower()
        vulns[severity] += 1
    return vulns


def read_report_image_size(report: Dict) -> int:
    return int(report["source"]["target"]["imageSize"])


def process_image(image: str, label: str) -> Dict:
    result = {}
    pull_image(image)
    scan_image(image, out_path=REPORT_PATH)
    with open(REPORT_PATH, "r") as fp_report:
        try:
            report = json.load(fp_report)
        except json.decoder.JSONDecodeError:
            print(f"An ERROR occured processing {image}.")
            return
        num_vulns = read_report_num_vulns(report)
        for k, v in num_vulns.items():
            result[f"{label}-{k}"] = v
        img_sz = read_report_image_size(report)
        result[f"{label}-img-sz"] = img_sz
    rm_image(image)
    return result


def process_chainguard_image(image_set_data: Dict, image_set: Dict) -> Dict:
    repo = image_set_data["repos"]["chainguard"]
    image = f"{repo}/{image_set['chainguard-latest']}"
    return process_image(image, "chainguard")


def process_rapidfort_image(image_set_data: Dict, image_set: Dict) -> Dict:
    repo = image_set_data["repos"]["rapidfort"]
    image = f"{repo}/{image_set['rapidfort-latest']}"
    return process_image(image, "rapidfort")


def process_docker_image(image_set_data: Dict, image_set: Dict) -> Dict:
    repo = image_set_data["repos"]["docker"]
    image = f"{repo}/{image_set['docker-latest']}"
    return process_image(image, "docker")


def process_alpine_image(image_set: Dict) -> Dict:
    image = image_set["alpine-full-name"]
    if image == "":
        return None
    return process_image(image, "alpine")


def main():
    df = pd.DataFrame()

    os.mkdir(TMP_DIR)

    with open(IMAGES_PATH, "r") as fp:
        image_set_data = json.load(fp)

        for image_set in image_set_data["images"]:
            row = {"image-name": image_set["name"]}

            result = process_chainguard_image(image_set_data, image_set)
            if result is not None:
                row.update(result)

            result = process_rapidfort_image(image_set_data, image_set)
            if result is not None:
                row.update(result)

            result = process_docker_image(image_set_data, image_set)
            if result is not None:
                row.update(result)

            result = process_alpine_image(image_set)
            if result is not None:
                row.update(result)
        
            df = pd.concat([df, pd.DataFrame(row, index=[0])], axis=0)

    df.to_csv(DATA_OUT_PATH)

    os.system(f"rm -rf {TMP_DIR}")


if __name__ == "__main__":
    main()