from typing import Dict
import json
import pandas as pd


SEVERITIES = ["unknown",
              "negligible",
              "low",
              "medium",
              "high",
              "critical"]


class ReportParserError(Exception):
    pass


class ReportParser:
    def __init__(self, report_path: str):
        self.report_path = report_path
        self.report_file_name = report_path.split("/")[-1]
        with open(report_path, "r") as fp:
            try:
                self.report = json.load(fp)
            except json.decoder.JSONDecodeError:
                raise ReportParserError
    
    def registry_domain(self) -> int:
        return self.report_file_name.split("_")[0]
    
    def registry_path(self) -> int:
        return self.report_file_name.split("_")[1]
    
    def image_name(self) -> int:
        return self.report_file_name.split("_")[2]
    
    def image_tag(self) -> int:
        return self.report_file_name.split("_")[3]
    
    def compare_id(self) -> int:
        return self.report_file_name.split("_")[4].split(".")[0]
    
    def ds(self) -> pd.DataFrame:
        raise NotImplementedError


class MetadataReportParser(ReportParser):
    def __init__(self, report_path: str):
        super().__init__(report_path)
    
    def image_size(self) -> int:
        try:
            return self.report["source"]["target"]["imageSize"]
        except KeyError:
            return 0
    
    def report_type(self) -> str:
        if self.registry_path() == "chainguard":
            return "chainguard"
        if self.registry_path() == "rapidfort":
            return "rapidfort"
        return "other"
    
    def ds(self) -> pd.DataFrame:
        metadata = {
            "registry_domain": self.registry_domain(),
            "registry_path": self.registry_path(),
            "image_name": self.image_name(),
            "image_tag": self.image_tag(),
            "compare_id": self.compare_id(),
            "image_size": self.image_size(),
            "report_type": self.report_type()
        }
        
        return pd.DataFrame(metadata, index=[0])
    

class GrypeReportParser(ReportParser):
    def __init__(self, report_path: str):
        super().__init__(report_path)
    
    def ds(self) -> pd.DataFrame:
        df = pd.DataFrame(columns=["registry_domain",
                                   "registry_path",
                                   "image_name",
                                   "image_tag",
                                   "severity",
                                   "type"])
        for match in self.report["matches"]:
            vdata = {
                "severity": match["vulnerability"]["severity"].lower(),
                "type": match["artifact"]["type"].lower()
            }

            vdata.update({
                "registry_domain": self.registry_domain(),
                "registry_path": self.registry_path(),
                "image_name": self.image_name(),
                "image_tag": self.image_tag(),
                "compare_id": self.compare_id(),
            })

            df = pd.concat([df, pd.DataFrame(vdata, index=[0])],
                           axis=0)
        return df


class SyftReportParser(ReportParser):
    def __init__(self, report_path: str):
        super().__init__(report_path)
    
    def ds(self) -> pd.DataFrame:
        df = pd.DataFrame(columns=["registry_domain",
                                   "registry_path",
                                   "image_name",
                                   "image_tag",
                                   "component_name",
                                   "type"])
        for art in self.report["artifacts"]:
            cdata = {
                "component_name": art["name"],
                "type": art["type"].lower()
            }
            
            # Skip for now: Few components have size data
            # if ("metadata" in art.keys()) and ("size" in art.keys()):
            #     cdata.update({
            #         "size": art["metadata"]["size"],
            #         "installedSize": art["metadata"]["installedSize"]
            #     })

            cdata.update({
                "registry_domain": self.registry_domain(),
                "registry_path": self.registry_path(),
                "image_name": self.image_name(),
                "image_tag": self.image_tag(),
                "compare_id": self.compare_id(),
            })

            df = pd.concat([df, pd.DataFrame(cdata, index=[0])],
                           axis=0)

        return df





    