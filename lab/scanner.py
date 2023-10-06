import os
import utils


class Scanner:
    def __init__(self, reports_dir: str):
        self.reports_dir = reports_dir
    
    def _report_filename(self, registry_domain: str,
                         registry_path: str, image_name: str,
                         tag: str, compare_id: str) -> str:
        if registry_path is None:
            registry_path = ""
        return "_".join([registry_domain,
                         registry_path,
                         image_name, tag,
                         compare_id]) + ".json"
    
    def _scan(self, image_full_name: str, out_path: str):
        raise NotImplemented
    
    def scan(self, registry_domain: str, registry_path: str,
             image_name: str, tag: str, compare_id: str):
        full_name = utils.image_full_name(registry_domain,
                                      registry_path, image_name,
                                      tag)
        filename = self._report_filename(registry_domain,
                                         registry_path, image_name,
                                         tag, compare_id)
        out_path = os.path.join(self.reports_dir, filename)
        self._scan(full_name, out_path)


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
