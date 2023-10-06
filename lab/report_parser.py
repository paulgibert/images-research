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
    
    def registry_type(self) -> int:
        return self.report_file_name.split("_")[0]
    
    def image_type(self) -> int:
        return self.report_file_name.split("_")[1].split(".")[0]
    
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
    
    def ds(self) -> pd.DataFrame:
        metadata = {
            "registry_type": self.registry_type(),
            "image_type": self.image_type(),
            "image_size": self.image_size(),
        }
        
        return pd.DataFrame(metadata, index=[0])
    

class GrypeReportParser(ReportParser):
    def __init__(self, report_path: str):
        super().__init__(report_path)
    
    def ds(self) -> pd.DataFrame:
        df = pd.DataFrame()
        for match in self.report["matches"]:
            vdata = {
                "severity": match["vulnerability"]["severity"].lower(),
                "type": match["artifact"]["type"].lower()
            }

            vdata.update({
                "registry_type": self.registry_type(),
                "image_type": self.image_type(),
            })

            df = pd.concat([df, pd.DataFrame(vdata, index=[0])],
                           axis=0)
        return df


class SyftReportParser(ReportParser):
    def __init__(self, report_path: str):
        super().__init__(report_path)
    
    def ds(self) -> pd.DataFrame:
        df = pd.DataFrame()
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
                "registry_type": self.registry_type(),
                "image_type": self.image_type(),
            })

            df = pd.concat([df, pd.DataFrame(cdata, index=[0])],
                           axis=0)

        return df





    