from typing import Dict
import os
import argparse
import json


IMAGES_PATH = os.path.join(os.path.dirname(__file__), "images.json")


def pull_image(image: str):
    cmd = f"docker pull {image}"
    os.system(cmd)


def scan_image(image: str, out_path: str):
    cmd = f"grype {image} -o json > {out_path}"
    os.system(cmd)


def rm_image(image: str):
    cmd = f"docker image rm {image}"
    os.system(cmd)


def get_report_fname(image: str) -> str:
    image_cleaned = image.replace("/", "-") \
                         .replace(":", "-") \
                         .replace(".", "")
    return image_cleaned + "-report.json"


def _process_image(image: str, report_dir: str) -> Dict:
    pull_image(image)
    out_path = os.path.join(report_dir, get_report_fname(image))
    scan_image(image, out_path=out_path)
    rm_image(image)


def process_chainguard_image(registries: Dict, images: Dict,
                             report_dir: str) -> Dict:
    reg = registries["chainguard"]
    img = f"{reg}/{images['chainguard-latest']}"
    _process_image(img, report_dir)


def process_rapidfort_image(registries: Dict, images: Dict,
                            report_dir: str) -> Dict:
    reg = registries["rapidfort"]
    img = f"{reg}/{images['rapidfort-latest']}"
    _process_image(img, report_dir)


def process_docker_image(registries: Dict, images: Dict,
                         report_dir: str) -> Dict:
    reg = registries["docker"]
    img = f"{reg}/{images['docker-latest']}"
    _process_image(img, report_dir)


def process_alpine_image(images: Dict,
                         report_dir: str) -> Dict:
    img = images["alpine-full-name"]
    if img != "":
        _process_image(img, report_dir)


def main():
    parser = argparse.ArgumentParser(
                    prog='collect_and_scan.py',
                    description='Pulls and scans docker images for analysis.')
    
    parser.add_argument("--report-dir", "-r",
                        required=True,
                        help="The directory to store scan reports.")
    
    report_dir = parser.parse_args().report_dir

    with open(IMAGES_PATH, "r") as fp:
        data = json.load(fp)
        registries = data["registries"]

        for images in data["images"]:
            process_chainguard_image(registries, images,
                                     report_dir)
            process_rapidfort_image(registries, images,
                                    report_dir)
            process_docker_image(registries, images,
                                 report_dir)
            process_alpine_image(images, report_dir)


if __name__ == "__main__":
    main()