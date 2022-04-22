import re

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
