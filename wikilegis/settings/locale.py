import django.conf.global_settings as default
from decouple import config
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(BASE_DIR)


LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'wikilegis/locale'),
]

languages = dict(default.LANGUAGES)
language_tuple = lambda language_code: (language_code,
                                        languages[language_code])

LANGUAGES = (
    language_tuple('en'),
    language_tuple('pt-br'),
    language_tuple('es'),
)

LANGUAGE_CODE = config('LANGUAGE_CODE', default='pt-br')
TIME_ZONE = config('TIME_ZONE', default='America/Sao_Paulo')
USE_I18N = True
USE_L10N = True
USE_TZ = True
