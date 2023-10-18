"""
Objects for scanning images with Grype and Syft.
Scans are saved to disk.
"""

import os
from src import utils


class ImageScanner:
    """
    A base class for scanning images and generating reports.
    """
    def __init__(self, reports_dir: str):
        """
        @param reports_dir: The directory to save scan reports.
        """
        self.reports_dir = reports_dir

    def _report_filename(self, vendor: str, image_type: str) -> str:
        """
        Returns a unique file name for the vendor and image type
        of the form {vendor}-{image_type}.
        For example: chainguard-nginx
        """
        return "_".join([vendor, image_type]) + ".json"

    def scan(self, image_fullname: str, report_path: str):
        """
        Abstract method that implementes scan logic and saves
        the report to report_path. This method is called by scan().
        Override this method in children.

        @param image_fullname: The full name of an image. Ex. docker.io/bitnami/nginx:latest
        @param report_path: The file path to save the report at.
        """
        raise NotImplementedError

    def scan_and_save(self, vendor: str, image_type: str,
                      image_fullname: str):
        """
        Scans the provided image and saves the report.

        @param vendor: The image vendor. Ex. chainguard
        @param image type: The image type. Ex. nginx
        @image_fullname: The full name of the image. Ex. docker.io/bitnami/nginx:latest
        """
        filename = self._report_filename(vendor, image_type)
        out_path = os.path.join(self.reports_dir, filename)
        self.scan(image_fullname, out_path)


class GrypeScanner(ImageScanner):
    """
    A class for scanning images and generating reports with Grype.
    """
    def scan(self, image_fullname: str, report_path: str):
        """
        Runs the Grype scanner.
        """
        cmd = f"grype {image_fullname} -o json > {report_path} 2> /dev/null"
        utils.bash(cmd)


class SyftScanner(ImageScanner):
    """
    A class for scanning images and generating reports with Syft.
    """

    def scan(self, image_fullname: str, report_path: str):
        """
        Runs the Syft scanner,
        """
        cmd = f"syft {image_fullname} -o syft-json > {report_path} 2> /dev/null"
        utils.bash(cmd)
