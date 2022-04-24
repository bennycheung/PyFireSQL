import re
import datetime
import json

class SQLDate():
  DATETIME_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"
  DATETIME_ISO_FORMAT_REGEX = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'

  match_iso8601 = re.compile(DATETIME_ISO_FORMAT_REGEX).match

  @classmethod
  def validate_iso8601(cls, str_val):
      try:            
          if SQLDate.match_iso8601( str_val ) is not None:
              return True
      except:
          pass
      return False


  @classmethod
  def document_to_json(cls, document, indent=2):
    def _convert_datetime(o):
      if isinstance(o, datetime.datetime):
        return o.strftime(SQLDate.DATETIME_ISO_FORMAT)

    json_str = json.dumps(document, indent=indent, default=_convert_datetime)
    return json_str


  @classmethod
  def json_to_document(cls, json_str):
    def _datetime_parser(dct):
      for k, v in dct.items():
          if isinstance(v, str) and SQLDate.DATETIME_ISO_FORMAT_REGEX.match(v):
              dct[k] = datetime.datetime.strptime(v, SQLDate.DATETIME_ISO_FORMAT)
      return dct

    document = json.loads(json_str, object_hook=_datetime_parser)
    return document

  @classmethod
  def value_to_string(cls, value):
    if isinstance(value, datetime.datetime):
      return value.strftime(SQLDate.DATETIME_ISO_FORMAT)
    elif isinstance(value, list):
      return [SQLDate.value_to_string(v) for v in value]
    elif isinstance(value, dict):
      dv = {}
      for k, v in value.items():
        dv[k] = SQLDate.value_to_string(v)
      return dv
    else:
      return value

  @classmethod
  def value_to_datetime(cls, value):
    if isinstance(value, str) and SQLDate.validate_iso8601(value):
      return datetime.datetime.fromisoformat(value)
    elif isinstance(value, list):
      return [SQLDate.value_to_datetime(v) for v in value]
    elif isinstance(value, dict):
      dv = {}
      for k, v in value.items():
        dv[k] = SQLDate.value_to_datetime(v)
      return dv
    else:
      return value

