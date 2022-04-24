import re
import json
import datetime
from .sql_date import SQLDate

class DocPrinter:
  """
  The DocPrinter class is for printing the select documents as CSV or JSON format output.

  Console output in the specified format.
  """
  def _get_field_value(self, doc, field):
    return doc.get(field, '')

  def value_conversion(self, value):
    if isinstance(value, datetime.datetime):
      return value.strftime(SQLDate.DATETIME_ISO_FORMAT)
    elif isinstance(value, list):
      return [self.value_conversion(v) for v in value]
    elif isinstance(value, dict):
      dv = {}
      for k, v in value.items():
        dv[k] = self.value_conversion(v)
      return dv
    else:
      return value

  def value_to_csv(self, value):
    if isinstance(value, str):
      return f'"{value}"'
    elif isinstance(value, list):
      convertList = []
      for v in value:
        if isinstance(v, str):
          cv = f'{v}'
        elif isinstance(v, list):
          cv = self.value_to_csv(v)
        elif isinstance(v, dict):
          cv = self.value_to_csv(v)
          # inside a list, remove the surronding quotes
          cv = cv.strip('"')
        else:
          cv = v
        convertList.append(cv)
      joinValue = ','.join(convertList)
      return f'"{joinValue}"'
    elif isinstance(value, dict):
      jsonValue = SQLDate.document_to_json(value)
      escapedJsonValue = jsonValue.replace('"', '\\"')
      return f'"{escapedJsonValue}"'
    else:
      return f"{value}"

  def printCSV(self, docs, selectFields):
    """
    printCSV is to print the given list of documents from the select fields in CSV output format

    Args:
      docs (List of documents as Dict): the list of documents after FireSQL select query
      selectFields (List of fields to output): the list of select fields to be picked out from each document (as Dict)

    Returns:
      str: string output in CSV format
    """
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
          values.append( self.value_conversion( self._get_field_value(doc, field) ) )
        else:
          values.append('')

      valuesList = []
      for value in values:
        valuesList.append( self.value_to_csv(value) )
      print(','.join( valuesList ))

  def printJSON(self, docs, selectFields):
    """
    printJSON is to print the given list of documents from the select fields in JSON output format

    Args:
      docs (List of documents as Dict): the list of documents after FireSQL select query
      selectFields (List of fields to output): the list of select fields to be picked out from each document (as Dict)

    Returns:
      str: string output in JSON format
    """
    print("[")
    count = 0
    total = len(docs)
    if '*' in selectFields:
      for key, doc in docs.items():
        count += 1
        fields = self.value_conversion(doc)
        comma = ',' if count < total else ''
        print('{}{}'.format( SQLDate.document_to_json(fields), comma ))
    else:
      for doc in docs:
        count += 1
        fields = {}
        for field in selectFields:
          if field in doc:
            fields[field] = self.value_conversion( self._get_field_value(doc, field) )
          else:
            fields[field] = ''
        comma = ',' if count < total else ''
        print('{}{}'.format( SQLDate.document_to_json(fields), comma ))
    print("]")
