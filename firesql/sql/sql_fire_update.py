from typing import Dict, List

from .sql_objects import (
  SQL_Update,
)

from .sql_fire_client import FireSQLAbstractClient
from .sql_fire_query import SQLFireQuery

class SQLFireUpdate(SQLFireQuery):

  def __init__(self):
    super(SQLFireUpdate, self).__init__()
    self.sets = {}

  def generate(self, update: SQL_Update, options: Dict = {}) -> Dict:
    self._init_update_collection_refs(update, options)
    self._init_update_sets(update)

    # create queries for each collections (parts)
    # return a dicitionary of {part -> [queries]}
    self.fireQueries = {}
    self._init_query_refs(update.where, fireQueries=self.fireQueries)
    return self.fireQueries

  def _init_update_collection_refs(self, update: SQL_Update, options: Dict = {}):
    table = update.table
    self.collections[table.part] = table.part
    self.aliases[table.part] = table.part
    if table.alias:
      self.aliases[table.alias] = table.part

    self.collectionFields[table.part] = ['docid', '*']

    self.defaultPart = next(iter(self.aliases))

  def _init_update_sets(self, update: SQL_Update):
    table = update.table
    self.sets[table.part] = {}
    for expr in update.sets:
      field = expr.left.column
      value = expr.right.value
      self.sets[table.part][field] = value

  def update_post_process(self, documents: Dict) -> List:
    docs = []
    if self.defaultPart in documents:
      targetDocs = documents[self.defaultPart]
      fields = self.collectionFields[self.defaultPart]
      fields = self._handle_star_fields(self.defaultPart, fields, targetDocs)
      for docId, doc in targetDocs.items():
        jdoc = {}
        for field in fields:
          if field == 'docid':
            jdoc['docid'] = docId
          elif field in self.sets[self.defaultPart]:
            jdoc[ self.columnNameMap[self.defaultPart][field] ] = self.sets[self.defaultPart][field]
          else:
            jdoc[ self.columnNameMap[self.defaultPart][field] ] = self._get_field_value(doc, field)
        docs.append(jdoc)

    return docs

  def update_execute(self, client: FireSQLAbstractClient, documents: List):
    docs = []
    if self.defaultPart in documents:
      targetDocs = documents[self.defaultPart]
      fields = self.collectionFields[self.defaultPart]
      fields = self._handle_star_fields(self.defaultPart, fields, targetDocs)
      for docId, doc in targetDocs.items():
        # jdoc for return list
        jdoc = {}
        # udoc for update
        updateDoc = {}
        for field in fields:
          if field == 'docid':
            jdoc['docid'] = docId
          elif field in self.sets[self.defaultPart]:
            jdoc[ self.columnNameMap[self.defaultPart][field] ] = self.sets[self.defaultPart][field]
            updateDoc[ self.columnNameMap[self.defaultPart][field] ] = self.sets[self.defaultPart][field]
          else:
            jdoc[ self.columnNameMap[self.defaultPart][field] ] = self._get_field_value(doc, field)
            updateDoc[ self.columnNameMap[self.defaultPart][field] ] = self._get_field_value(doc, field)
        docs.append(jdoc)

        # execute update to docId
        if updateDoc:
          client.update_collection_document(self.defaultPart, docId, updateDoc)

    return docs
