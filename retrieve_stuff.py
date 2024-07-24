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
chars_in_tier = {}

for tier_table in tier_tables:
    tier = tier_table.find("tr").find_all('th')[0].get_text()
    print(f"tier: {tier}")

    try:
        counter = 0
        for tier_entry in tier_table.find("td"):
            char_name = tier_entry.find("span", {"class": "tier-servant-name-span"}).get_text()

            if counter == 0:
                chars_in_tier[tier] = [char_name]
                counter += 1

            else:
                chars_in_tier[tier] += [char_name]

            print(tier_entry)
            
    except Exception as e:
        logger.error(e)

print(chars_in_tier)
print(len(chars_in_tier.values()))

# close the webdriver instance
driver.quit()

