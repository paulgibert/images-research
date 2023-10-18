"""
Objects for parsing Grype and Syft scan reports.
"""


import json
import pandas as pd


class ReportParserError(Exception):
    """
    An Exception class for errors related to report parsing.
    """


class ReportParser:
    """
        A generic base class for report parsing.
    """

    def __init__(self, report_path: str):
        """
        @param report_path: The path of the report to parse
        @raises ReportParserError if report cannot be decoded by json
        """
        self.report_path = report_path
        self.report_file_name = report_path.split("/")[-1]
        with open(report_path, "r", encoding="utf-8") as fp:
            try:
                self.report = json.load(fp)
            except json.decoder.JSONDecodeError as e:
                raise ReportParserError from e

    def image_vendor(self) -> str:
        """
        @returns the image vendor. Ex. chainguard
        """
        return self.report_file_name.split("_")[0]

    def image_type(self) -> str:
        """
        @returns the image type. Ex. nginx
        """
        return self.report_file_name.split("_")[1].split(".")[0]

    def ds(self) -> pd.DataFrame:
        """
        Abstract method that returns parsed report data as a pandas
        DataFrame. Override this method in children.

        @returns parsed report in a pandas DataFrame
        """
        raise NotImplementedError


class GrypeMetadataReportParser(ReportParser):
    """
    A class for parsing metadata, such as image size,
    from Grpye reports. This parser does not provide
    vulnerability data.
    """

    def image_size(self) -> int:
        """
        @returns the image size.
        """
        try:
            return self.report["source"]["target"]["imageSize"]
        except KeyError:
            return 0

    def image_digest(self, n: int=None) -> str:
        """
        @param n: Only return the first n characters of the digest.
        @returns the image digest.
        """
        try:
            digest = self.report["source"]["target"]["manifestDigest"]
            digest = digest.split(":")[1]
            if n is None:
                return digest
            return digest[:n]
        except KeyError:
            return "???"

    def ds(self) -> pd.DataFrame:
        """
        @returns parsed image size data as a pandas DataFrame.

        The DataFrame takes the form

        |  image_vendor  |  image_type  | image_size_bytes | image_digest |
        ===================================================================
        |   chainguard   |     nginx    |     180123891    |     f012b1   |
        |   rapidfort    |     nginx    |     140233827    |     cd6dc2   |
        ...

        """
        metadata = {
            "image_vendor": self.image_vendor(),
            "image_type": self.image_type(),
            "image_size_bytes": self.image_size(),
            "image_digest": self.image_digest(n=6)
        }

        return pd.DataFrame(metadata, index=[0])


class GrypeReportParser(ReportParser):
    """
    A class for parsing Grpye reports.
    """

    def ds(self) -> pd.DataFrame:
        """
        @returns parsed vulnerability data as a pandas DataFrame.

        The DataFrame takes the form

        |   image_vendor |  image_type  | severity | type |
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
                "image_vendor": self.image_vendor(),
                "image_type": self.image_type(),
            })

            df = pd.concat([df, pd.DataFrame(vdata, index=[0])],
                           axis=0)
        return df


class SyftReportParser(ReportParser):
    """
    A class for parsing Syft reports.
    """

    def ds(self) -> pd.DataFrame:
        """
        Returns parsed vulnerability data as a pandas DataFrame.

        The DataFrame takes the form

        |  image_vendor  |  image_type  |       name        | type |
        ============================================================
        |   chainguard   |     nginx    | alpine-baselayout | apk  | 
        |   chainguard   |     redis    |    alpine-keys    | apk  |
        ...

        """
        df = pd.DataFrame()
        for art in self.report["artifacts"]:
            cdata = {
                "name": art["name"],
                "type": art["type"].lower()
            }

            cdata.update({
                "image_vendor": self.image_vendor(),
                "image_type": self.image_type(),
            })

            df = pd.concat([df, pd.DataFrame(cdata, index=[0])],
                           axis=0)

        return df
