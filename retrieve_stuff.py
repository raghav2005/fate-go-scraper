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

# setup chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # ensure GUI is off
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# setup chrome driver with webdriver manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
# url of the webpage to scrape
url = "https://fgo.gamepress.gg/servant-tier-list"

# load the webpage
driver.get(url)
logger.success(f"requested webpage: {url}")

def get_QAB_from_HTML_class(list_of_HTML_classes):
    for HTML_class in list_of_HTML_classes:
        if "npinfobox" in HTML_class:
            return HTML_class.split('-')[1][0].upper()

    return "Unknown"

try:
    # wait until the desired element is present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "view-content"))
    )
    logger.success("webpage loaded")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    logger.success("parsed webpage")

except Exception as e:
    logger.error(e)

tier_tables = soup.find_all("table", {"class": "fgo-tier-table"})
chars_in_tier = defaultdict(list)

for tier_table in tier_tables:
    tier = tier_table.find("tr").find_all('th')[0].get_text()
    print(f"tier: {tier}")

    try:
        for tier_entry in tier_table.find("td"):
            char_name = tier_entry.find("span", {"class": "tier-servant-name-span"}).get_text()

            char_tier_np_info = tier_entry.find("div", {"class": "FGOTierNPInfo"})
            char_rarity = len(char_tier_np_info.find("span", {"class": "star-rarity"}).get_text())
            char_type = char_tier_np_info.find("div").get_text()
            char_NP_QAB = get_QAB_from_HTML_class(char_tier_np_info.get("class"))

            char_summary = tier_entry.find("div", {"class": "tier-expl-container"}).get_text()

            char_urls = tier_entry.find("div", {"class": "FGOTierServantIcon"})
            char_page_url = char_urls.find("a").get("href").split('/')[-1]
            char_img_url = char_urls.find("img").get("src")

            chars_in_tier[tier].append({
                "name": char_name,
                "rarity": char_rarity,
                "summary": char_summary,
                "type": char_type,
                "NP_QAB": char_NP_QAB,
                "img_url": char_img_url,
                "servant_page_partial_url": char_page_url
            })

    except Exception as e:
        logger.error(e)

print(chars_in_tier)

# close the webdriver instance
driver.quit()
