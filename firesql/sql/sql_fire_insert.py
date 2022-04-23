import datetime
from typing import Dict, List

from .sql_objects import (
  SQL_Insert,
  SQL_ValueJSON,
)

from .sql_date import SQLDate
from .sql_fire_client import FireSQLAbstractClient


# internal firebase insert
class SQLFireInsert():

  def __init__(self):
    self.clear()

  def clear(self):
    self.part = None
    self.columns = []
    self.values = []
    self.result = {}

  def generate(self, insert: SQL_Insert, options: Dict = {}):
    self.part = insert.table.part

    for colRef in insert.columns:
      self.columns.append(colRef.column)

    for valueRef in insert.values: 
      value = valueRef.value
      if isinstance(value, str) and SQLDate.validate_iso8601(value):
        value = datetime.datetime.fromisoformat(value)
      self.values.append(value)

    # if number of columns do not match the number of values
    if len(self.columns) != len(self.values):
      return False

    return True

  def select_fields(self) -> List:
    fields = ['docid']
    for field in self.columns:
      fields.append(field)
    return fields

  def execution_result(self) -> Dict:
    return self.result

  def post_process(self) -> Dict:
    doc = {}
    if '*' in self.columns:
      # if star is specified as the column, only JSON dict can be inserted
      # the first level of JSON dict keys are inserted into doc.
      for value in self.values:
        if isinstance(value, Dict):
          for key in value.keys():
            doc[key] = value[key]
      # transfer all the keys to columns specification
      self.columns = [key for key in doc]
    else:
      # process as a corresponding (column, value) pair
      for idx in range(len(self.columns)): 
        doc[ self.columns[idx] ] = self.values[idx]
    return doc

  def execute(self, client: FireSQLAbstractClient, document: Dict) -> Dict:
    docId = client.generate_collection_document_id(self.part)
    if docId:
      self.result = client.set_collection_document(self.part, docId, document)

    # assign docid back to document and return
    document['docid'] = docId
    return document
