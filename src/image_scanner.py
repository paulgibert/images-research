import os


class ImageScanner:
    def __init__(self, reports_dir: str):
        """
        A base class for scanning images and generating reports.
        """
        self.reports_dir = reports_dir
    
    def _report_filename(self, provider: str, flavor: str) -> str:
        """
        Returns a unique file name for the provider and flavor.
        """
        return "_".join([provider, flavor]) + ".json"
    
    def _scan(self, image_path: str, report_path: str):
        """
        Abstract method that implementes scan logic and saves
        the report to report_path. This method is called by scan().
        Override this method in children.

        @param image_path: The full path of an image. Ex. docker.io/bitnami/nginx:latest
        @param report_path: The file path to save the report at.
        """
        raise NotImplemented
    
    def scan(self, provider: str, flavor: str,
             image_path: str):
        """
        Scans the provided image and saves the report.

        @param provider: The provider of the image. Ex. chainguard
        @param flavor: The image flavor. Ex. nginx
        @image_path: The full path of an image. Ex. docker.io/bitnami/nginx:latest
        """
        filename = self._report_filename(provider,
                                         flavor)
        out_path = os.path.join(self.reports_dir, filename)
        self._scan(image_path, out_path)


class GrypeScanner(ImageScanner):
    def __init__(self, reports_dir: str):
        """
        A class for scanning images and generating reports with Grype.
        """
        super().__init__(reports_dir)
    
    def _scan(self, image_path: str, report_path: str):
        cmd = f"grype {image_path} -o json > {report_path}"
        os.system(cmd)


class SyftScanner(ImageScanner):
    def __init__(self, reports_dir: str):
        """
        A class for scanning images and generating reports with Syft.
        """
        super().__init__(reports_dir)
    
    def _scan(self, image_path: str, report_path: str):
        cmd = f"syft {image_path} -o syft-json > {report_path}"
        os.system(cmd)
