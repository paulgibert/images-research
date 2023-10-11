import os
import sys

# Add parent dir to path
sys.path.append("/".join(os.path.dirname(__file__).split("/")[0:-1]))

from typing import List
import argparse
import json
from src.image_scanner import ImageScanner, GrypeScanner, SyftScanner

IMAGES_JSON_PATH = os.path.join(
                        os.path.dirname(
                                os.path.abspath(__file__)), "images.json")
GRYPE_DIRNAME = "grype"
SYFT_DIRNAME = "syft"


class ImageProcessor:
    def __init__(self, scanners: List[ImageScanner]):
        """
        A class for applying a list scanners to an image and
        generating reports.

        @param scanners: A list of ImageScanners to apply to the image.
        """
        if scanners is None:
            scanners = []
        self.scanners = scanners
    
    def _image_path(self, provider_domain: str, image_path: str,
                    image_tag: str) -> str:
        """
        Returns the full path to an image.
        Ex. docker.io/bitnami/nginx:latest
        """
        return f"{provider_domain}/{image_path}:{image_tag}"
    
    def process(self, provider: str, flavor: str,
                provider_domain: str, image_path: str,
                image_tag: str):
        """
        Apply all scanners to the provide image.
        """
        if len(self.scanners) == 0:
            print("Zero scanners specified. Nothing to do.")
            return
        
        image_path = self._image_path(provider_domain, image_path,
                                      image_tag)

        for sc in self.scanners:
            sc.scan(provider, flavor, image_path)


def parse_args() -> str:
    parser = argparse.ArgumentParser(
                    prog='1_scan_images.py',
                    description='Pulls and scans a list of images with Grype and Syft.')
    
    parser.add_argument("--reports-dir", "-r",
                        required=True,
                        help="The directory to save scan reports.")

    reports_dir = parser.parse_args().reports_dir
    
    return reports_dir
        

def main():
    reports_dir = parse_args()

    grype_dir = os.path.join(reports_dir, GRYPE_DIRNAME)
    syft_dir = os.path.join(reports_dir, SYFT_DIRNAME)

    # Create environment to save reports to
    for d in [grype_dir, syft_dir]:
        os.mkdir(d)

    proc = ImageProcessor(scanners=[GrypeScanner(grype_dir), 
                                    SyftScanner(syft_dir)])
    
    # Parse the images.json file and process all images
    with open(IMAGES_JSON_PATH, "r") as fp:
        for flavor in json.load(fp)["flavors"]:
            for provider in flavor["providers"]:
                proc.process(provider["name"],
                             flavor["name"],
                             provider["domain"],
                             provider["path"],
                             provider["tag"])


if __name__ == "__main__":
    main()
        
    
