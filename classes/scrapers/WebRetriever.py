from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger


class WebRetriever:
    def __init__(self, url, debug=False):
        self.url = url
        self.debug = debug
        self.driver = None

    def setup_selenium_driver(self):
        # setup chrome options for selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # ensure GUI is off
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # setup chrome driver with webdriver manager
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )

    # msg_type: one of ["success", "error", "trace", "info", "warning", "critical", "debug"]
    def log(self, msg, msg_type="success"):
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

    def load_webpage(self, url=None):
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
