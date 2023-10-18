import json
import pdb
import re
import time
from selenium import webdriver
import tabulate
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


XPATH_OTHER = "/html/body/div[1]/div[2]/div/div/div/div[2]/div[1]/div[1]/div[3]/div/div/p"
XPATH_OFFICIAL = "/html/body/div[1]/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/div/div[2]/p"
         

def dhub_url(path: str, vendor: str) -> str:
    if vendor is None:
        url = f"https://hub.docker.com/_/{path}"
    else:
        url = f"https://hub.docker.com/r/{path}"
    return url


def _get_xpath_pulls(url: str, xpath: str, driver) -> str:
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH, xpath)))
    p = driver.find_element(By.XPATH, xpath)
    return p.text


def _get_regex_pulls(url: str, driver) -> str:
    driver.get(url)
    time.sleep(2)
    html = driver.page_source
    x = re.search("\d+[KMB]\+", html)
    if x is None:
        return "?"
    return x.string[x.start(): x.end()]


def dhub_official_pulls(image: str, driver) -> str:
    url = f"https://hub.docker.com/_/{image}"
    return _get_regex_pulls(url, driver)


def dhub_other_pulls(image: str, driver) -> str:
    url = f"https://hub.docker.com/r/{image}"
    return _get_regex_pulls(url, driver)


def main():
    options = Options() 
    options.add_argument("-headless") 
    # driver = webdriver.Firefox(options=None)

    df = pd.DataFrame()
    with open("scripts/images.json", "r") as fp:
        flavors = json.load(fp)["flavors"]
        for flvr in flavors:
            for prov in flvr["providers"]:
                if prov["name"] == "original":
                    if "bitnami" in prov["path"]:
                        pulls = "?"
                        # pulls = dhub_other_pulls(prov["path"], driver)
                    else:
                        pulls = "?"
                        # pulls = dhub_official_pulls(prov["path"], driver)
                elif prov["name"] == "rapidfort":
                    pulls = "?"
                    # pulls = dhub_other_pulls(prov["path"], driver)
                else:
                    pulls = "?"
                    # print(f"Error: {flvr['name']}/{prov['name']}")
                    # continue
                
                df = pd.concat([df, pd.DataFrame({
                    "image_provider": prov["name"],
                    "image_flavor": flvr["name"],
                    "pulls": pulls
                }, index=[0])], axis=0)

    df2 = pd.read_csv("data/analysis/digests.csv")
    df = df.merge(df2, how="left", on=["image_provider", "image_flavor"]) \
           .groupby(["image_provider", "image_flavor", "image_digest", "pulls"]).count()
    df = df.drop("Unnamed: 0", axis=1)
    df.to_csv("table.csv")


if __name__ == "__main__":
    main()