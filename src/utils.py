import logging

import requests

logger = logging.getLogger(__name__)


class HtmlSiteBasicParser:
    def __init__(self, url):
        self.url = url

    def load_page(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            return response.content
        logger.error(f"Couldn't load page {self.url}")
        return None


class PDFBasicParser(HtmlSiteBasicParser):
    def __init__(self, url: str, location: str):
        HtmlSiteBasicParser.__init__(self, url=url)
        self.location = location

    def download_pdf(self):
        pdf = self.load_page()
        if pdf:
            with open(self.location, "wb") as f:
                f.write(pdf)
            logger.info(f"data written to {self.location}")
        else:
            logger.error("Could not load pdf")

    def load_pdf(self):
        with open(self.location, "r") as f:
            return f
