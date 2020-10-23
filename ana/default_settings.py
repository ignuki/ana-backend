import os
from schema import Schema, And, Use, Optional
from datetime import timedelta


def parse_bool(s: str):
   return s.lower() in ('yes', 'true', 't', '1')


class Config:
   DEBUG = parse_bool(os.getenv('DEBUG', '0'))
   TESTING = parse_bool(os.getenv('TESTING', '0'))
   ENV = 'production'
   PREFERRED_URL_SCHEME = os.getenv('PREFERRED_URL_SCHEME', 'http')

   APPLICATION_ROOT = '/'

   USE_X_SENDFILE = parse_bool(os.getenv('USE_X_SENDFILE', '0'))
   MAX_CONTENT_LENGTH = None
   SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=43200)

   PROPAGATE_EXCEPTIONS= None
   TRAP_BAD_REQUEST_ERRORS = None
   TRAP_HTTP_EXCEPTIONS = parse_bool(os.getenv('TRAP_HTTP_EXCEPTIONS', '0'))
   PRESERVE_CONTEXT_ON_EXCEPTION = None

   JSON_AS_ASCII = parse_bool(os.getenv('JSON_AS_ASCII', '1'))
   JSON_SORT_KEYS = parse_bool(os.getenv('JSON_SORT_KEYS', '1'))
   JSONIFY_PRETTYPRINT_REGULAR = parse_bool(
      os.getenv('JSON_PRETTYPRINT_REGULAR', '0')
   )
   JSONIFY_MIMETYPE = 'application/json'

   TEMPLATES_AUTO_RELOAD = None
   EXPLAIN_TEMPLATE_LOADING = parse_bool(
      os.getenv('EXPLAIN_TEMPLATE_LOADING', '0')
   )

   PLAYER_MEDIA_DIR = os.getenv('PLAYER_MEDIA_DIR', '/tmp/media')
   PLAYER_DEFAULT_SHUF_DIR = os.getenv('PLAYER_DEFAULT_SHUF_DIRECTORY', 'series')
