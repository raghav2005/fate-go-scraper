from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from loguru import logger
from collections import defaultdict

class WebRetriever:
    def __init__(self, url, debug = False):
        self.url = url
        self.debug = debug
        
    def setup_selenium_driver(self):
        # setup chrome options for selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # ensure GUI is off
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # setup chrome driver with webdriver manager
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # msg_type: one of ["success", "error", "trace", "info", "warning", "critical", "debug"]
    def log(self, msg, msg_type = "success"):
        if self.debug:
            # match msg_type:
            #     case "success":
            #         logger.success(msg)
            #     case "error":
            #         logger.error(msg)
            #     case "trace":
            #         logger.trace(msg)
            #     case "info":
            #         logger.info(msg)
            #     case "warning":
            #         logger.warning(msg)
            #     case "critical":
            #         logger.critical(msg)
            #     case default:
            #         logger.debug(msg)

            try:
                getattr(logger, msg_type)(msg)
            except Exception as e:
                logger.error(e)

        else:
            if msg_type in ["error", "critical"]:
                getattr(logger, msg_type)(msg)
    
    def load_webpage(self, url = None):
        if url is None:
            url = self.url

        # setup drivers
        self.setup_selenium_driver()

        # load the webpage
        self.driver.get(url)
        self.log(f"requested webpage: {url}", "debug")
        
    def quit_webdriver(self):
        # close the webdriver instance
        self.driver.quit()

class FGOWebRetriever(WebRetriever):
    def __init__(self, url, debug=False):
        super().__init__(url, debug)
        self.chars_in_tier = self.get_tier_list_info()

    def get_QAB_from_HTML_class(self, list_of_HTML_classes):
        for HTML_class in list_of_HTML_classes:
            if "npinfobox" in HTML_class:
                return HTML_class.split('-')[1][0].upper()

        self.log("Unknown NP QAB", "warning")
        return "Unknown"

    def get_tier_list_info(self):
        self.load_webpage()

        try:
            # wait until content is present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "view-content"))
            )

            self.log("webpage loaded")
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            self.log("parsed webpage", "debug")

            tier_tables = soup.find_all("table", {"class": "fgo-tier-table"})
            chars_in_tier = defaultdict(list)

            for tier_table in tier_tables:
                tier = tier_table.find("tr").find_all('th')[0].get_text()
                self.log(f"tier: {tier}", "info")

                for tier_entry in tier_table.find("td"):
                    try:
                        char_name = tier_entry.find("span", {"class": "tier-servant-name-span"}).get_text()

                        char_tier_np_info = tier_entry.find("div", {"class": "FGOTierNPInfo"})
                        char_rarity = len(char_tier_np_info.find("span", {"class": "star-rarity"}).get_text())
                        char_type = char_tier_np_info.find("div").get_text()
                        char_NP_QAB = self.get_QAB_from_HTML_class(char_tier_np_info.get("class"))

                        char_summary = tier_entry.find("div", {"class": "tier-expl-container"}).get_text()

                        char_urls = tier_entry.find("div", {"class": "FGOTierServantIcon"})
                        char_page_url = char_urls.find("a").get("href").split('/')[-1]
                        char_img_url = char_urls.find("img").get("src")

                        char_info = {
                            "name": char_name,
                            "rarity": char_rarity,
                            "summary": char_summary,
                            "type": char_type,
                            "NP_QAB": char_NP_QAB,
                            "img_url": char_img_url,
                            "servant_page_partial_url": char_page_url
                        }
                        chars_in_tier[tier].append(char_info)
                        self.log(char_info, "debug")

                    except Exception as e:
                        self.log(f"Error processing entry: {e}", "error")

            self.quit_webdriver()
            return chars_in_tier

        except Exception as e:
            self.log(f"Error retrieving tier list info: {e}", "error")
            self.quit_webdriver()            
            return defaultdict(list)


if __name__ == "__main__":
    url = "https://fgo.gamepress.gg/servant-tier-list"
    fgo_scraper = FGOWebRetriever(url, debug = True)
    # fgo_scraper.log(fgo_scraper.chars_in_tier, "debug")
