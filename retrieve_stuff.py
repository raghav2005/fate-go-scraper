from classes.scrapers import FGOWebRetriever

if __name__ == "__main__":
    url = "https://fgo.gamepress.gg/servant-tier-list"
    fgo_scraper = FGOWebRetriever(url, debug=True)
    # fgo_scraper.log(fgo_scraper.chars_in_tier, "debug")
