from typing import List
import os
import argparse
import json
from scanner import Scanner
from scanner import GrypeScanner, SyftScanner
import utils


IMAGES_JSON_PATH = os.path.join(
                        os.path.dirname(
                                os.path.abspath(__file__)), "images.json")
GRYPE_DIRNAME = "grype"
SYFT_DIRNAME = "syft"

class ImageProcessor:
    def __init__(self, scanners: List[Scanner]):
        if scanners is None:
            scanners = []
        self.scanners = scanners

    def _rm_image(self, image_full_name: str):
        cmd = f"docker image rm {image_full_name}"
        os.system(cmd)
    
    def process(self, registry_type: str, image_type: str,
                registry_domain: str, registry_path: str,
                image_name: str, tag: str):
        if len(self.scanners) == 0:
            print("0 scanners specified. Nothing to do!")
            return
        
        full_name = utils.image_full_name(registry_domain, registry_path,
                                          image_name, tag)

        for sc in self.scanners:
            sc.scan(registry_type, image_type, full_name)
            
        self._rm_image(full_name)


def parse_reports_dir() -> str:
    parser = argparse.ArgumentParser(
                    prog='scan_images.py',
                    description='Pulls and scans a list of images.')
    
    parser.add_argument("--reports-dir", "-r",
                        required=True,
                        help="The directory to save scan reports.")

    reports_dir = parser.parse_args().reports_dir
    
    return reports_dir
        

def main():
    reports_dir = parse_reports_dir()

    grype_dir = os.path.join(reports_dir, GRYPE_DIRNAME)
    syft_dir = os.path.join(reports_dir, SYFT_DIRNAME)

    os.mkdir(grype_dir)
    os.mkdir(syft_dir)

    proc = ImageProcessor(scanners=[
            GrypeScanner(grype_dir),
            SyftScanner(syft_dir)])
    
    with open(IMAGES_JSON_PATH, "r") as fp:
        for image in json.load(fp)["images"]:
            for registry in image["registries"]:
                proc.process(registry["name"],
                             image["name"],
                             registry["domain"],
                             registry["path"],
                             registry["image_name"],
                             registry["tag"])


if __name__ == "__main__":
    main()
        
    
