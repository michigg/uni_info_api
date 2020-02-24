from datetime import datetime, timedelta
import re

import config
import PyPDF2

from utils import PDFBasicParser

DATE_REGEX = "([0-9]{2}.[0-9]{2}.[0-9]{4}){1,2}"

FILE_LOCATION = "./tmp/info.pdf"


class UniInfoParser(PDFBasicParser):
    def __init__(self, url=config.DETAIL_DEADLINES_APPOINTMENTS_URL, pdf_location=FILE_LOCATION):
        PDFBasicParser.__init__(self, url=self.get_current_url(url), location=pdf_location)

    @staticmethod
    def get_current_url(url):
        date = datetime.now().date()
        if config.SUMMER_SEMESTER_LIMITS[1] < date.month < config.SUMMER_SEMESTER_LIMITS[2]:
            semester_token = date.strftime("SS_%Y")
        else:
            if config.SUMMER_SEMESTER_LIMITS[1] < date.month:
                semester_token = date.strftime("WS_%y-") + date.replace(year=date.year + 1).strftime("%y")
            else:
                token_end = date.strftime("%y")
                semester_token = date.replace(year=date.year - 1).strftime("WS_%y-") + token_end
        return f'{url}/{semester_token}.pdf'

    def save_info_data(self):
        self.download_pdf()

    def get_info(self):
        with open(self.location, "rb") as f:
            text = self._extract_text(f)

        text_arr = str(text).split(" ")
        cleaned_text_arr = [elem.replace("\n", "") for elem in text_arr]
        cleaned_text_arr = [elem.lower() for elem in cleaned_text_arr if elem]
        print(" ".join(cleaned_text_arr))

        semester_range = self._get_date_range(cleaned_text_arr, "verwaltungszeitraum")
        semester_lecture_range = self._get_date_range(cleaned_text_arr, "vorlesungszeiten")
        free_times_section = self._get_arr_between_from_to_keyword(cleaned_text_arr, "tage", "termine")
        free_times = self._get_free_times(free_times_section)
        semester_notify = self._get_date_range(cleaned_text_arr, "rückmeldung")
        data = {"semester_range": semester_range, "lecture_times": semester_lecture_range,
                "lecture_free_times": free_times, "reregistration": semester_notify}
        return data

    def _extract_text(self, file):
        pdfReader = PyPDF2.PdfFileReader(file)
        pageObject = pdfReader.getPage(0)
        text = pageObject.extractText()
        return text

    def _get_date_range(self, data: [], label: str) -> []:
        start_index = data.index(label) + 1
        start = data[start_index]
        stop = data[start_index + 1]
        return [self._iso_date(start), self._iso_date(stop)]

    def _get_date(self, data: []) -> str or []:
        concated = " ".join(data)
        matches = re.findall(DATE_REGEX, concated)
        return [self._iso_date(date) for date in matches]

    def _get_free_times(self, data: [], list_indicator="-"):
        indices = [i for i, x in enumerate(data) if x == list_indicator]
        last_index = -1
        free_times = []
        for index in indices:
            if last_index > -1:
                free_time = self._get_date(data[last_index + 1:index])
                free_times.append(free_time)
            last_index = index
        free_time = self._get_date(data[last_index + 1:])
        free_times.append(free_time)
        return free_times

    def _get_arr_between_from_to_keyword(self, data: [], key_from: str, key_to: str):
        from_id = data.index(key_from) + 1
        to_id = data.index(key_to)
        return data[from_id:to_id]

    def _iso_date(self, pdf_date: str):
        return datetime.strptime(pdf_date, "%d.%m.%Y").strftime("%Y-%m-%d")

    def is_lecture_time(self, uni_infos):
        lecture_times = uni_infos["lecture_times"]
        lecture_end_date = datetime.strptime(lecture_times[1], "%Y-%m-%d").date()
        lecture_start_date = datetime.strptime(lecture_times[0], "%Y-%m-%d").date()
        today = datetime.today().date()
        # today = datetime.strptime("2019-12-25", "%Y-%m-%d").date()

        return self.is_in_date_range(lecture_start_date, lecture_end_date, today)

    def is_free_time(self, uni_infos):
        lecture_free_times = uni_infos["lecture_free_times"]
        is_free = False
        today = datetime.today().date()
        # today = datetime.strptime("2019-12-25", "%Y-%m-%d").date()
        for time in lecture_free_times:
            if len(time) == 2:
                free_start = datetime.strptime(time[0], "%Y-%m-%d").date()
                free_end = datetime.strptime(time[1], "%Y-%m-%d").date()
                is_free = self.is_in_date_range(free_start, free_end, today)
            else:
                free_date = datetime.strptime(time[0], "%Y-%m-%d").date()
                if free_date == today:
                    is_free = True
        return is_free

    def is_in_date_range(self, start_date: datetime.date, end_date: datetime.date,
                         to_proof_date: datetime.date) -> bool:
        return start_date <= to_proof_date <= end_date


if "__main__" == __name__:
    parser = UniInfoParser()
    print(parser.get_current_url(config.DETAIL_DEADLINES_APPOINTMENTS_URL))
