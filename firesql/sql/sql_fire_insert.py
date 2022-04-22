import datetime
from typing import Dict, List

from .sql_objects import (
  SQL_Insert,
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
  
  def build(self) -> Dict:
    doc = {}
    for idx in range(len(self.columns)): 
      doc[ self.columns[idx] ] = self.values[idx]
    return doc

  def execute(self, client: FireSQLAbstractClient, document: Dict) -> Dict:
    docId = client.generate_collection_document_id(self.part)
    if docId:
      client.set_collection_document(self.part, docId, document)

    # assign docid back to document and return
    document['docid'] = docId
    return document
