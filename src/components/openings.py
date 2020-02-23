import re

from bs4 import BeautifulSoup

import config
from utils import HtmlSiteBasicParser


class OpeningHours(HtmlSiteBasicParser):
    def __init__(self, url=config.OPENING_HOURS_URL):
        HtmlSiteBasicParser.__init__(self, url=url)

    def get_opening_hours(self):
        html = self.load_page()
        soup = BeautifulSoup(html, 'html.parser')
        time_blocks = soup.find_all("div", {"class": "headline-block__wrapper"})

        openings_in_lectures = self._get_building_opening_times(time_blocks[0])
        openings_out_lectures = self._get_building_opening_times(time_blocks[1])
        return {"openings_during_lectures": openings_in_lectures,
                "openings": openings_out_lectures,
                "source": config.OPENING_HOURS_URL}

    def _get_building_opening_times(self, time_block):
        openings = []
        p_tags = time_block.find_all("p")
        for p_tag in p_tags:
            match = re.findall(config.TIMES_REGEX, p_tag.text)
            if len(match) > 0:
                opening = self._get_opening(match)
                openings.append(opening)
        return openings

    def _get_opening(self, match):
        times = str(match[0][5]).split("-")
        start_time = times[0]  # datetime.strptime(times[0], "%H%H.%M%M")
        end_time = times[1]  # datetime.strptime(times[1], "%H%H.%M%M")
        opening = {"location": match[0][0],
                   "start_weekday": match[0][3],
                   "end_weekday": match[0][4],
                   "start_time": start_time,
                   "end_time": end_time}
        return opening
