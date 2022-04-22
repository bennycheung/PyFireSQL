from typing import Dict, List

from .sql_objects import (
  SQL_Delete,
)

from .sql_fire_client import FireSQLAbstractClient
from .sql_fire_query import SQLFireQuery

class SQLFireDelete(SQLFireQuery):

  def __init__(self):
    super(SQLFireDelete, self).__init__()
    self.sets = {}

  def generate(self, delete: SQL_Delete, options: Dict = {}) -> Dict:
    self._init_delete_collection_refs(delete, options)

    # create queries for each collections (parts)
    # return a dicitionary of {part -> [queries]}
    self.fireQueries = {}
    self._init_query_refs(delete.where, fireQueries=self.fireQueries)
    return self.fireQueries

  def _init_delete_collection_refs(self, delete: SQL_Delete, options: Dict = {}):
    table = delete.table
    self.collections[table.part] = table.part
    self.aliases[table.part] = table.part
    if table.alias:
      self.aliases[table.alias] = table.part

    self.collectionFields[table.part] = ['docid', '*']

    self.defaultPart = next(iter(self.aliases))

  def delete_post_process(self, documents: Dict) -> List:
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
          else:
            jdoc[ self.columnNameMap[self.defaultPart][field] ] = self._get_field_value(doc, field)
        docs.append(jdoc)

    return docs

  def delete_execute(self, client: FireSQLAbstractClient, documents: List):
    docs = []
    if self.defaultPart in documents:
      targetDocs = documents[self.defaultPart]
      fields = self.collectionFields[self.defaultPart]
      fields = self._handle_star_fields(self.defaultPart, fields, targetDocs)
      for docId, doc in targetDocs.items():
        # jdoc for return list
        jdoc = {}
        for field in fields:
          if field == 'docid':
            jdoc['docid'] = docId
          else:
            jdoc[ self.columnNameMap[self.defaultPart][field] ] = self._get_field_value(doc, field)
        docs.append(jdoc)

        # execute update to docId
        if jdoc:
          client.delete_collection_document(self.defaultPart, docId)

    return docs
