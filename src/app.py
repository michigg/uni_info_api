import datetime

import camelot
from celery import Celery
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restplus import Api, Resource

import config
from components.exam_appointments import ExamParser, cache, FILE_LOCATION
from components.info import UniInfoParser
from components.openings import OpeningHours
from utils import PDFBasicParser

import logging

logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

if config.PROD_MODE:
    cache.init_app(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': config.CACHE_REDIS_URL})
    logger.warning("Use production mode logging")
else:
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})

api = Api(app=app, doc='/docs', version='1.0', title='Uni Information API',
          description='Collect data from not direkt computable data sources like pdf or html and extract the informations to a json format')

app.config['CELERY_BROKER_URL'] = config.CELERY_REDIS_URL
app.config['CELERY_RESULT_BACKEND'] = config.CELERY_REDIS_URL

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

examParser = ExamParser()
opening_hours = OpeningHours()
uni_info_parser = UniInfoParser()


def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return (path + args)


@api.route(f'{config.API_V1_ROOT}exams/')
class ExamsApi(Resource):

    def get(self):
        """
        returns Exam appointments
        """
        load_exam_appointments()
        return jsonify(examParser.get_exam_appointments())


@cache.cached(timeout=config.CACHE_DURATION_OPENING_HOURS)
@api.route(f'{config.API_V1_ROOT}openings/')
class OpeningsApi(Resource):

    def get(self):
        """
        returns Building Opening Hours
        """
        uni_info_parser.save_info_data()
        uni_infos = uni_info_parser.get_info()
        if "lecture_times" in uni_infos:
            data = opening_hours.get_opening_hours()
            if not uni_info_parser.is_lecture_time(uni_infos):
                return jsonify({"opening_hours": data["openings"], "source": data["source"]})
            else:
                return jsonify({"opening_hours": data["openings_during_lectures"], "source": data["source"]})
        return jsonify([])


@cache.cached(timeout=config.CACHE_DURATION_INFO)
@api.route(f'{config.API_V1_ROOT}info/')
class InfoApi(Resource):

    def get(self):
        """
        returns university informations like semester start and end
        """
        uni_info_parser.save_info_data()
        return jsonify(uni_info_parser.get_info())


# @cache.cached(timeout=config.CACHE_DURATION_INFO)
@api.route(f'{config.API_V1_ROOT}info/today/')
class InfoTodayApi(Resource):

    def get(self):
        """
        returns university bool informations free day, lecture day
        """
        uni_info_parser.save_info_data()
        uni_infos = uni_info_parser.get_info()
        if "lecture_times" in uni_infos:
            return jsonify({"is_lecture_day": uni_info_parser.is_lecture_time(uni_infos=uni_infos),
                            "is_free_day": uni_info_parser.is_free_time(uni_infos=uni_infos),
                            "source": uni_info_parser.url})


@cache.cached(timeout=config.CACHE_DURATION_EXAM_PDF, key_prefix='exam_appointments_download')
def load_exam_appointments():
    background_load_exam_appointments.apply_async()
    return []


@celery.task
def background_load_exam_appointments():
    pdf_parser = PDFBasicParser(url=ExamParser.get_current_url(config.EXAM_APPOINTMENTS), location=FILE_LOCATION)
    pdf_parser.download_pdf()
    tables = camelot.read_pdf(FILE_LOCATION, pages="1-end")
    table_json_base_location = "./tmp/camelot/jsons"
    tables.export(f'{table_json_base_location}/exam.json', f="json")


if __name__ == '__main__':
    app.run()
