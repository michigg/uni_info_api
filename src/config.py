import os

API_V1_ROOT = "/api/v1/"
PROD_MODE = os.environ.get("PROD_MODE", "False") == "TRUE"
CACHE_REDIS_URL = os.environ.get("CACHE_REDIS_URL", None)
CELERY_REDIS_URL = os.environ.get("CELERY_REDIS_URL", None)
CACHE_DURATION_EXAM_PDF = 24 * 60 * 60 * 60
CACHE_DURATION_EXAM_RESULT = 60 * 60
CACHE_DURATION_INFO = 60 * 60
CACHE_DURATION_OPENING_HOURS = 60 * 60 * 12

SUMMER_SEMESTER_LIMITS = [4, 9]

# EXAM ENDPOINT
EXAM_APPOINTMENTS = "https://www.uni-bamberg.de/fileadmin/uni/verwaltung/pruefungsaemter/dateien/Pruefungsamt_I"
EXAM_REGEX = r"(?P<date>[0-9]{2}.[0-9]{2}.[0-9]{2})(?P<time>[0-9]{2}:[0-9]{2})(?P<room>[A-ZÄÖÜ0-9]{1,4}\/[0-9Kk-]{1,2}.[0-9a-z]{2,3}|[A-Za-zß]*( [0-9]*)*)(?P<name_initials>\n[A-Z] - [A-Z])*(?P<additional_info>\n\w*( \w*)*)*\n(?P<exam_type>BA, MA|BA, LA|MA|BA)"
ROOM_REGEX = r"(?P<building_key>[A-ZÄÖÜ0-9]{1,3})\/(?P<room_level>[0-9kK\-]{1,2}).(?P<room_number>[0-9a-z]{1,4})"

# BUILDING OPENING HOURS ENDPOINT
OPENING_HOURS_URL = "https://www.uni-bamberg.de/universitaet/anreise/oeffnungszeiten/"
TIMES_REGEX = r"(?P<location>[a-zA-Zßäüö1-9() ]*)(:|: )((?P<weekdays>Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag) - (Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag)): (?P<time>[0-9]{1,2}.[0-9]{2} - [0-9]{1,2}.[0-9]{2}) Uhr"

#
DEADLINES_APPOINTMENTS_URL = "https://www.uni-bamberg.de/studium/im-studium/studienorganisation/vorlesungszeiten/"
DETAIL_DEADLINES_APPOINTMENTS_URL = "https://www.uni-bamberg.de/fileadmin/uni/verwaltung/studentenkanzlei/dateien"
