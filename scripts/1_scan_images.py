"""
Stage 1 script.
Performs Grype and Syft scans on images listed in scripts/images.json.
Scan reports are saved to the directroy specified.

Usage:
    1_scan_images.py -r [report directory]

Example:
    1_scan_images.py -r data/scans
"""


from typing import List
import os
import sys
import argparse
import json

# Add parent dir to path
sys.path.append("/".join(os.path.dirname(__file__).split("/")[0:-1]))

from src.image_scanner import GrypeScanner, SyftScanner
from src import utils


IMAGES_JSON_PATH = os.path.join(
                   os.path.dirname(
                   os.path.abspath(__file__)), "images.json")
GRYPE_DIRNAME = "grype"
SYFT_DIRNAME = "syft"


def get_image_fullname(domain: str, path: str,
                   tag: str) -> str:
    """
    Returns the full name of an image of the form
    [domain]/[path]:[tag].
    
    For example:
    domain = docker.io,
    path = bitnami/nginx
    tag = latest

    returns:
    docker.io/bitnami/nginx:latest
    
    @param domain: The domain of the vendor registry
    @param path: The path the image can be found at
    @param tag: The tag of the image.
    """
    return f"{domain}/{path}:{tag}"


def _rm_image(image_fullname: str):
    """
    Removes an image locally

    @param image_fullname: The full name of an image. Ex. cgr.dev/chianguard/nginx:latest
    """
    cmd = f"docker image rm {image_fullname}"
    utils.bash(cmd)


def process_image(vendor: str, image_type: str,
                  image_fullname: str, scanners: List=None):
    """
    Apply all scanners to the provide image.

    @param vendor: The image vendor. Ex chainguard.
    @param image_type: The type of image. Ex nginx.
    @param image_fullname: The fullname of th image.
                           Ex cgr.dev/chainguard/nginx:latest
    @param scanners: A List of scanners to apply to each image.
    """
    if scanners is None:
        scanners = []

    if len(scanners) == 0:
        print("Zero scanners specified. Nothing to do.")
        return

    for sc in scanners:
        sc.scan_and_save(vendor=vendor,
                         image_type=image_type,
                         image_fullname=image_fullname)
        _rm_image(image_fullname)


def parse_args() -> str:
    """
    Parses script args.
    """
    parser = argparse.ArgumentParser(
                    prog=os.path.basename(__file__),
                    description="Pulls and scans a list of images with Grype and Syft.")
    parser.add_argument("--reports-dir", "-r",
                        required=True,
                        help="The directory to save scan reports.")

    reports_dir = parser.parse_args().reports_dir
    return reports_dir


def main():
    """
    The main method of the script.
    Scans the images found in images.json with Grype and Syft.
    """
    reports_dir = parse_args()

    grype_dir = os.path.join(reports_dir, GRYPE_DIRNAME)
    syft_dir = os.path.join(reports_dir, SYFT_DIRNAME)

    # Create a sub directory to save reports to
    for d in [grype_dir, syft_dir]:
        utils.mkdir(d)

    # Define Grype and Syft scanners
    scanners = [
        GrypeScanner(grype_dir),
        SyftScanner(syft_dir)]

    # Parse the images.json file and process all images
    with open(IMAGES_JSON_PATH, "r", encoding="utf-8") as fp:
        for image in json.load(fp)["images"]:
            for vendor in image["vendors"]:
                image_fullname = get_image_fullname(vendor["domain"],
                                                    vendor["path"],
                                                    vendor["tag"])
                process_image(vendor=vendor["name"],
                              image_type=image["name"],
                              image_fullname=image_fullname,
                              scanners=scanners)


if __name__ == "__main__":
    main()
