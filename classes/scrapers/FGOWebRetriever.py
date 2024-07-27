from classes.scrapers import WebRetriever

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from collections import defaultdict

class FGOWebRetriever(WebRetriever):
    def __init__(self, url, debug=False):
        super().__init__(url, debug)
        self.chars_in_tier = self.get_tier_list_info()

    @staticmethod
    def get_QAB_from_HTML_class(list_of_HTML_classes):
        for HTML_class in list_of_HTML_classes:
            if "npinfobox" in HTML_class:
                return HTML_class.split("-")[1][0].upper()

        self.log("Unknown NP QAB", "warning")
        return "Unknown"

    def get_tier_list_info(self):
        self.load_webpage()

        try:
            # wait until content is present
            WebDriverWait(self.driver, 10).until(
                # EC.presence_of_element_located((By.CLASS_NAME, "view-content"))
                EC.presence_of_element_located((By.CLASS_NAME, "fgo-tier-table"))
            )

            self.log("webpage loaded")
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            self.log("parsed webpage", "debug")

            tier_tables = soup.find_all("table", {"class": "fgo-tier-table"})
            chars_in_tier = defaultdict(list)

            for tier_table in tier_tables:
                tier = tier_table.find("tr").find_all("th")[0].get_text()
                self.log(f"tier: {tier}", "info")

                for tier_entry in tier_table.find("td"):
                    try:
                        char_name = tier_entry.find(
                            "span", {"class": "tier-servant-name-span"}
                        ).get_text()

                        char_tier_np_info = tier_entry.find(
                            "div", {"class": "FGOTierNPInfo"}
                        )
                        char_rarity = len(
                            char_tier_np_info.find(
                                "span", {"class": "star-rarity"}
                            ).get_text()
                        )
                        char_type = char_tier_np_info.find("div").get_text()
                        char_NP_QAB = self.get_QAB_from_HTML_class(
                            char_tier_np_info.get("class")
                        )

                        char_summary = tier_entry.find(
                            "div", {"class": "tier-expl-container"}
                        ).get_text()

                        char_urls = tier_entry.find(
                            "div", {"class": "FGOTierServantIcon"}
                        )
                        char_page_url = char_urls.find("a").get("href").split("/")[-1]
                        char_img_url = char_urls.find("img").get("src")

                        char_info = {
                            "name": char_name,
                            "rarity": char_rarity,
                            "summary": char_summary,
                            "type": char_type,
                            "NP_QAB": char_NP_QAB,
                            "img_url": char_img_url,
                            "servant_page_partial_url": char_page_url,
                        }
                        chars_in_tier[tier].append(char_info)
                        self.log(char_info, "debug")

                    except Exception as e:
                        self.log(f"Error processing entry: {e}", "error")

            return chars_in_tier

        except Exception as e:
            self.log(f"Error retrieving tier list info: {e}", "error")
            return defaultdict(list)

        finally:
            self.quit_webdriver()
