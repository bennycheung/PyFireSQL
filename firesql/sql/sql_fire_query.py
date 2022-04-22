import datetime
from typing import Dict, List

from .sql_objects import (
  SQL_Select,
  SQL_BinaryExpression,
  SQL_JoinExpression,
  SQL_ColumnRef,
  SQL_SelectFrom,
)
from .sql_join import JoinPart, FireSQLJoin
from .sql_aggregation import FireSQLAggregate

from .sql_date import SQLDate
from .sql_fire_client import FireSQLAbstractClient


# internal firebase query
class SQLFireQuery():

  def __init__(self):
    self.clear()

  def clear(self):
    self.columns = []
    self.columnNameMap = {}
    self.collections = {}
    self.aliases = {}
    self.collectionFields= {}
    self.aggregationFields={}
    self.on = None

  def generate(self, select: SQL_Select, options: Dict = {}) -> Dict:
    self._init_collection_refs(select, options)
    self._init_field_refs(select, options)
    self._init_column_names()
    # create queries for each collections (parts)
    # return a dicitionary of {part -> [queries]}
    self.fireQueries = {}
    self._init_query_refs(select.where, fireQueries=self.fireQueries)
    return self.fireQueries

  def _init_collection_refs(self, select: SQL_Select, options: Dict = {}):
    for table in select.froms:
      if isinstance(table, SQL_JoinExpression):
        joinTables = [table.left, table.right]
        for join in joinTables:
          self.collections[join.part] = join.part
          self.aliases[join.part] = join.part
          if join.alias:
            self.aliases[join.alias] = join.part
        # ON must be done after the join tables has been defined
        if table.on:
          leftRef: SQL_ColumnRef = table.on.left
          rightRef: SQL_ColumnRef = table.on.right
          self.on = [
              (self.aliases[leftRef.table], leftRef.column),
              table.on.operator,
              (self.aliases[rightRef.table], rightRef.column)
            ]
      else:
        self.collections[table.part] = table.part
        self.aliases[table.part] = table.part
        if table.alias:
          self.aliases[table.alias] = table.part
    self.defaultPart = next(iter(self.aliases))
  
  def _init_field_refs(self, select: SQL_Select, options: Dict = {}):
    self.columns = select.columns
    for sel in select.columns:
      if sel.table:
        partName = self.aliases[sel.table]
      else:
        # no table name, get the first table name
        partName = self.aliases[self.defaultPart]

      if partName not in self.collectionFields:
        self.collectionFields[partName] = []
        self.aggregationFields[partName] = []

      self.collectionFields[partName].append(sel.column)

      # if there is an aggregation function on column
      if sel.func:
        self.aggregationFields[partName].append( (sel.func, sel.column) )

  def _init_query_refs(self, query: SQL_BinaryExpression, fireQueries={}):
    if query:
      if query.operator in ('and', 'or'):
        self._init_query_refs(query.left, fireQueries=fireQueries)
        self._init_query_refs(query.right, fireQueries=fireQueries)
      else:
        leftRef = query.left
        rightRef = query.right

        if isinstance(rightRef, List):
          valList = [v.value for v in rightRef]
          fireQuery = [leftRef.column, query.operator, valList]
        elif isinstance(rightRef, SQL_ColumnRef):
          fireQuery = [leftRef.column, query.operator, rightRef.column]
        else:
          if rightRef:
            value = rightRef.value
          else:
            value = None
          if isinstance(value, str) and SQLDate.validate_iso8601(value):
            value = datetime.datetime.fromisoformat(value)
          fireQuery = [leftRef.column, query.operator, value]

        if leftRef.table:
          partName = self.aliases[leftRef.table]
        else:
          partName = self.aliases[self.defaultPart]

        if partName not in fireQueries:
          fireQueries[partName] = []

        fireQueries[partName].append(fireQuery)

  def _init_column_names(self):
    self.columnNameMap = {}
    colNames = [c.column for c in self.columns]
    for ci in range(len(colNames)):
      tableName = self.aliases[ self.columns[ci].table ] if self.columns[ci].table else self.defaultPart
      if tableName not in self.columnNameMap:
        self.columnNameMap[ tableName ] = {}
      self.columnNameMap[ tableName ][ colNames[ci] ] = self.columns[ci].column
      for cj in range(ci+1, len(colNames)):
        if colNames[ci] == colNames[cj]:
          # rename ambiguous column by renaming to table_column
          self.columnNameMap[ tableName ][ colNames[ci] ] = '_'.join( [self.columns[ci].table, self.columns[ci].column] )

  def firebase_queries(self, allQueries: Dict) -> Dict:
    fireQueries = {}
    if allQueries:
      for part in allQueries.keys():
        fireQueries[part] = []
        for query in allQueries[part]:
          (_, operator, _) = query
          if operator not in ['like', 'not_like']:
            fireQueries[part].append(query)
    return fireQueries

  def filter_queries(self, allQueries: Dict) -> Dict:
    filterQueries = {}
    if allQueries:
      for part in allQueries.keys():
        filterQueries[part] = []
        for query in allQueries[part]:
          (_, operator, _) = query
          if operator in ['like', 'not_like']:
            filterQueries[part].append(query)
    return filterQueries

  def execute(self, client: FireSQLAbstractClient, fireQueries: Dict) -> Dict:
    documents = {}
    if fireQueries:
      for part in fireQueries.keys():
        collectionName = self.collections[part]
        if fireQueries[part]:
          documents[part] = client.query_document_by_where_tuples(collectionName, fireQueries[part])
        else:
          documents[part] = client.get_collection_documents(collectionName)
    else:
      collectionName = self.collections[self.defaultPart]
      documents[self.defaultPart] = client.get_collection_documents(collectionName)
    return documents

  def filter_documents(self, documents, filterQueries: Dict) -> Dict:
    if filterQueries:
      filterDocs = {}
      for part in filterQueries.keys():
        if filterQueries[part]:
          filterDocs[part] = {}
          for filter in filterQueries[part]:
            (field, operator, pattern) = filter
            pattern = pattern.replace('%', '.*')
            matchPattern = re.compile(pattern).match
            if operator == 'like':
              for docId, doc in documents[part].items():
                if field in doc and matchPattern(doc[field]):
                  filterDocs[part][docId] = doc
            elif operator == 'not_like':
              for docId, doc in documents[part].items():
                if field in doc and not matchPattern(doc[field]):
                  filterDocs[part][docId] = doc
        else:
          filterDocs[part] = documents[part]
      return filterDocs
    else:
      return documents
    
  def select_fields(self) -> List:
    fields = []
    if FireSQLAggregate.hasAggregation(self.aggregationFields):
      for part in self.aggregationFields.keys():
        if self.aggregationFields[part]:
          for func, column in self.aggregationFields[part]:
            fieldName = FireSQLAggregate.fieldName(func, column)
            fields.append(fieldName)
    else:
      # check if any field is ambiguous, rename it to become table_column
      for c in self.columns:
        if c.column != '*':
          tableName = c.table if c.table else self.defaultPart
          fields.append(self.columnNameMap[ self.aliases[tableName] ][ c.column ])
    return fields

  def _handle_star_fields(self, tableName: str, fields: List, documents: Dict) -> List:
    if '*' in fields:
      if documents:
        # find all the fields from a sample document
        firstDocKey = next(iter(documents))
        doc = documents[firstDocKey]
        # integrate all document fields into the field list
        # but skip the '*' field
        jfields = []
        for field in fields:
          if field != '*':
            jfields.append(field)
        for field in doc.keys():
          if field not in fields:
            jfields.append(field)
        fields = jfields

        # update the columns and column name map for the table
        if tableName not in self.columnNameMap:
          self.columnNameMap[ tableName ] = {}
        for key in sorted(fields):
          self.columnNameMap[ tableName ][key] = key
          self.columns.append( SQL_ColumnRef(table=tableName, column=key, func=None ))

    return fields

  def _get_field_value(self, doc, field):
    tokens = field.split('.')
    if len(tokens) == 1:
      return doc.get(field, '')
    else:
      # loop through the subfields to reach the lowest value
      dd = doc
      for f in tokens:
        dd = dd.get(f, '')
        if not dd:
          break
      return dd

  def _get_join_part(self, documents: Dict, partRef: SQL_SelectFrom, isStar: bool = False):
    part, field = partRef
    docs = documents[part]
    if isStar:
      fields = ['*']
    else:
      fields = self.collectionFields[part]
    fields = self._handle_star_fields(part, fields, docs)
    nameMap = self.columnNameMap[part]
    return JoinPart(docs=docs, joinField=field, selectFields=fields, nameMap=nameMap)

  def post_process(self, documents: Dict) -> List:
    docs = []
    if self.on:
      # there is join, unpack the join-on operator
      leftRef, operator, rightRef = self.on
      leftPart, _ = leftRef
      leftFields = self.collectionFields[leftPart]
      isStar = True if '*' in leftFields else False
      # get left part
      leftJoinPart = self._get_join_part(documents, leftRef, isStar=isStar)
      # get right part
      rightJoinPart = self._get_join_part(documents, rightRef, isStar=isStar)

      joinOp = FireSQLJoin()
      docs = joinOp.inner_join(leftJoinPart, rightJoinPart)

    else:
      # there is no join
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

  def aggregation(self, documents: Dict) -> List:
    if FireSQLAggregate.hasAggregation(self.aggregationFields):
      fireAggregate = FireSQLAggregate()
      return fireAggregate.aggregation(self.aggregationFields, documents)
    else:
      return documents

