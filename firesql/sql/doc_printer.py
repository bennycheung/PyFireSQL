import re
import json
import datetime

class DocPrinter:
  DATETIME_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"
  DATETIME_ISO_FORMAT_REGEX = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'

  match_iso8601 = re.compile(DATETIME_ISO_FORMAT_REGEX).match

  @classmethod
  def validate_iso8601(cls, str_val):
      try:            
          if DocPrinter.match_iso8601( str_val ) is not None:
              return True
      except:
          pass
      return False

  def __init__(self):
    pass

  def document_to_json(self, document):
    def _convert_datetime(o):
      if isinstance(o, datetime.datetime):
        return o.strftime(DocPrinter.DATETIME_ISO_FORMAT)

    json_str = json.dumps(document, default=_convert_datetime)
    return json_str

  def value_conversion(self, value):
    if isinstance(value, datetime.datetime):
      return value.strftime(DocPrinter.DATETIME_ISO_FORMAT)
    elif isinstance(value, list):
      return [self.value_conversion(v) for v in value]
    elif isinstance(value, dict):
      return self.document_to_json(value)
    else:
      return value

  def printCSV(self, docs, selectFields):
    if '*' in selectFields:
      # sample a doc for all the fields
      firstKey = next(iter(docs))
      doc = docs[firstKey]
      selectFields = doc.keys()

    print(','.join([f'"{f}"' for f in selectFields]))
    for doc in docs:
      values = []
      for field in selectFields:
        if field in doc:
          values.append(self.value_conversion(doc[field]))
        else:
          values.append('')
      valuesList = [f'"{v}"' if (isinstance(v, str) and v != '') else f'{v}' for v in values]
      print(','.join( valuesList ))

  def printJSON(self, docs, selectFields):
    print("[")
    if '*' in selectFields:
      for key, doc in docs.items():
        print('{},'.format(self.document_to_json(doc)))
    else:
      for doc in docs:
        fields = {}
        for field in selectFields:
          if field in doc:
            fields[field] = self.value_conversion(doc[field])
          else:
            fields[field] = ''
        print('{},'.format(fields))
    print("]")
