import json
import pandas as pd


class ReportParserError(Exception):
    """
    An Exception class for errors related to report parsing.
    """
    pass


class ReportParser:
    def __init__(self, report_path: str):
        """
        A generic base class for report parsing.
        """
        self.report_path = report_path
        self.report_file_name = report_path.split("/")[-1]
        with open(report_path, "r") as fp:
            try:
                self.report = json.load(fp)
            except json.decoder.JSONDecodeError:
                raise ReportParserError
    
    def image_provider(self) -> str:
        """
        Returns the image provider.
        """
        return self.report_file_name.split("_")[0]
    
    def image_flavor(self) -> str:
        """
        Returns the image flavor.
        """
        return self.report_file_name.split("_")[1].split(".")[0]
    
    def ds(self) -> pd.DataFrame:
        """
        Abstract method that returns parsed report data as a pandas
        DataFrame. Override this method in children.
        """
        raise NotImplementedError


class MetadataReportParser(ReportParser):
    def __init__(self, report_path: str):
        """
        A class for parsing metadata from Grpye reports.
        """
        super().__init__(report_path)
    
    def image_size(self) -> int:
        """
        Returns the image size.
        """
        try:
            return self.report["source"]["target"]["imageSize"]
        except KeyError:
            return 0
    
    def image_digest(self, n=6) -> str:
        try:
            digest = self.report["source"]["target"]["manifestDigest"]
            return digest.split(":")[1][:n]
        except KeyError:
            return "None"
    
    def ds(self) -> pd.DataFrame:
        """
        Returns parsed image size data as a pandas DataFrame.

        The DataFrame takes the form

        | image_provider | image_flavor | image_size_bytes | image_digest |
        ===================================================================
        |   chainguard   |     nginx    |     180123891    |     f012b1   |
        |   rapidfort    |     nginx    |     140233827    |     cd6dc2   |
        ...

        """
        metadata = {
            "image_provider": self.image_provider(),
            "image_flavor": self.image_flavor(),
            "image_size_bytes": self.image_size(),
            "image_digest": self.image_digest()
        }
        
        return pd.DataFrame(metadata, index=[0])
    

class GrypeReportParser(ReportParser):
    def __init__(self, report_path: str):
        """
        A class for parsing Grpye reports.
        """
        super().__init__(report_path)
    
    def ds(self) -> pd.DataFrame:
        """
        Returns parsed vulnerability data as a pandas DataFrame.

        The DataFrame takes the form

        | image_provider | image_flavor | severity | type |
        ===================================================
        |   chainguard   |     nginx    |   high   |  apk |
        |   rapidfort    |     nginx    |   low    |  deb |
        ...

        """
        df = pd.DataFrame()
        for match in self.report["matches"]:
            vdata = {
                "severity": match["vulnerability"]["severity"].lower(),
                "type": match["artifact"]["type"].lower()
            }

            vdata.update({
                "image_provider": self.image_provider(),
                "image_flavor": self.image_flavor(),
            })

            df = pd.concat([df, pd.DataFrame(vdata, index=[0])],
                           axis=0)
        return df


class SyftReportParser(ReportParser):
    def __init__(self, report_path: str):
        """
        A class for parsing Syft reports.
        """
        super().__init__(report_path)
    
    def ds(self) -> pd.DataFrame:
        """
        Returns parsed vulnerability data as a pandas DataFrame.

        The DataFrame takes the form

        | image_provider | image_flavor |       name        | type |
        ============================================================
        |   chainguard   |     nginx    | alpine-baselayout | apk  | 
        |   chainguard   |     redis    |    alpine-keys    | apk  |
        ...

        """
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
                "image_provider": self.image_provider(),
                "image_flavor": self.image_flavor(),
            })

            df = pd.concat([df, pd.DataFrame(cdata, index=[0])],
                           axis=0)

        return df