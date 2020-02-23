import json
import re
from datetime import datetime
from os import listdir
from os.path import isfile, join

from flask_caching import Cache

import config
from utils import PDFBasicParser

FILE_LOCATION = "./tmp/exam.pdf"

cache = Cache()


class ExamParser(PDFBasicParser):
    def __init__(self, url=config.EXAM_APPOINTMENTS, pdf_location=FILE_LOCATION,
                 table_json_base_location="./tmp/camelot/jsons"):
        PDFBasicParser.__init__(self, url=self.get_current_url(url), location=pdf_location)
        self.table_json_base_location = table_json_base_location

    @staticmethod
    def get_current_url(url):
        date = datetime.now().date()
        if config.SUMMER_SEMESTER_LIMITS[1] < date.month < config.SUMMER_SEMESTER_LIMITS[2]:
            semester_token = date.strftime("SS_%y_mit_Raeumen_und_Uhrzeiten")
        else:
            if config.SUMMER_SEMESTER_LIMITS[1] < date.month:
                semester_token = date.strftime("PTPlan_WS_%Y_") + date.replace(year=date.year + 1).strftime(
                    "%y_mit_Raeumen_und_Uhrzeiten")
            else:
                token_end = date.strftime("%y_mit_Raeumen_und_Uhrzeiten")
                semester_token = date.replace(year=date.year - 1).strftime("PTPlan_WS_%Y_") + token_end
        return f'{url}/{semester_token}.pdf'

    # @cache.cached(timeout=config.CACHE_DURATION_EXAM_PDF, key_prefix='exam_appointments_download')
    # def load_exam_appointments(self):
    #     thread = Thread(target=background_load_exam_appointments)
    #     thread.daemon = True
    #     thread.start()

    # def background_load_exam_appointments(self):
    #     self.download_pdf()
    #     tables = camelot.read_pdf(self.location, pages="1-end")
    #     tables.export(f'{self.table_json_base_location}/exam.json', f="json")

    @cache.cached(timeout=config.CACHE_DURATION_EXAM_RESULT, key_prefix='exam_appointments')
    def get_exam_appointments(self):
        table_jsons = [f for f in listdir(self.table_json_base_location) if
                       isfile(join(self.table_json_base_location, f))]
        prepared_json = []
        for table_json in table_jsons:
            json_file = self._load_json_table(self.table_json_base_location, table_json)
            self._load_table_exams(json_file, prepared_json)
        print(prepared_json)
        return prepared_json

    def _load_table_exams(self, json_file, prepared_json):
        for row in json_file:
            appointment = self._extract_exam_appointment(row)
            if appointment:
                prepared_json.append(appointment)

    def _extract_exam_appointment(self, row):
        regex = r"[0-9]{2}.[0-9]{2}.[0-9]{2}"
        pattern = re.compile(regex)
        if pattern.findall(row["0"]) and (
                "entfällt" not in str(row["2"]).lower() or "entfällt" not in str(row["1"]).lower()):
            duration = self._get_duration(row)
            return {
                "date": datetime.strptime(row["0"], "%d.%m.%y").strftime("%Y-%m-%d"),
                "time": row["1"],
                "room": row["2"], "type": row["3"],
                "degree": row["4"], "short": row["5"],
                "lecture": row["6"],
                "minutes_duration": duration,
                "chair": row["7"],
            }
        return None

    def _load_json_table(self, dir: str, table_json_file_name: str):
        with open(f'{dir}/{table_json_file_name}', "r") as f:
            return json.load(f)

    def _get_duration(self, elem):
        duration_regex = r'.*(?P<duration>[0-9]{2,3}).*(Minuten|Miunten).*'
        results = re.findall(duration_regex, elem["6"], re.DOTALL)
        duration = 0
        if results:
            print(results[0][0])
            duration = int(results[0][0])
            print(duration)
        elif "4h-klausur" in str(elem["6"]).lower():
            duration = 240
        return duration
