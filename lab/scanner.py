import os


class Scanner:
    def __init__(self, reports_dir: str):
        self.reports_dir = reports_dir
    
    def _report_filename(self, registry_type: str, image_type: str) -> str:
        return "_".join([registry_type, image_type]) + ".json"
    
    def _scan(self, image_full_name: str, out_path: str):
        raise NotImplemented
    
    def scan(self, registry_type: str, image_type: str,
             image_full_name: str):
        filename = self._report_filename(registry_type,
                                         image_type)
        out_path = os.path.join(self.reports_dir, filename)
        self._scan(image_full_name, out_path)


class GrypeScanner(Scanner):
    def __init__(self, reports_dir: str):
        super().__init__(reports_dir)
    
    def _scan(self, image_full_name: str, out_path: str):
        cmd = f"grype {image_full_name} -o json > {out_path}"
        os.system(cmd)


class SyftScanner(Scanner):
    def __init__(self, reports_dir: str):
        super().__init__(reports_dir)
    
    def _scan(self, image_full_name: str, out_path: str):
        cmd = f"syft {image_full_name} -o syft-json > {out_path}"
        os.system(cmd)
