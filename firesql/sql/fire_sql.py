import os
from pathlib import Path
from typing import Dict, List

from lark import Lark

from .sql_objects import (
  SQL_Select,
  SQL_Insert,
  SQL_Update,
  SQL_Delete,
)
from .sql_transformer import SQLTransformer

from .sql_fire_client import FireSQLAbstractClient
from .sql_fire_query import SQLFireQuery
from .sql_fire_update import SQLFireUpdate
from .sql_fire_insert import SQLFireInsert
from .sql_fire_delete import SQLFireDelete


_ROOT = Path(__file__).parent
try:
  GRAMMAR_PATH = os.path.join(_ROOT, "grammar", "firesql.lark")
  with open(file=GRAMMAR_PATH) as sql_grammar_file:
    _GRAMMAR_TEXT = sql_grammar_file.read()
except:
  GRAMMAR_PATH = os.path.join(".", "grammar", "firesql.lark")
  with open(file=GRAMMAR_PATH) as sql_grammar_file:
    _GRAMMAR_TEXT = sql_grammar_file.read()


# main interface
class FireSQL():
  """
  FireSQL is the main programming interface to execute FireSQL statements

  During FireSQL initialization, the FireSQL parser is prepared from `sql/grammar/firesql.lark`.
  """

  def __init__(self):
    self.transformer = SQLTransformer()
    self.parser = Lark(_GRAMMAR_TEXT, parser="lalr")

  def select_fields(self) -> List:
    """
    From the parsed FireSQL select statement, return the select fields.

    Args:
      None
    Returns:
      The list of select fields as strings
    """
    return self.sqlFireCommand.select_fields()

  def sql(self, client: FireSQLAbstractClient, sql: str, options: Dict = {}) -> List:
    """
    Given a Firebase connection, execute the FireSQL statement.

    Args:
      client (FirebaseClient): The client has established a Firebase connection
      sql (str): FireSQL statement to be executed
      options (Dist): Unused

    Returns:
      docs: A list of selected documents
    """
    try:
      # select statement SQL parser to produce the AST
      ast = self.parser.parse(sql)
      # transform AST into parsed SQL components
      sqlCommand = self.transformer.transform(ast)
    except Exception as e:
      print('Parseing Error: {}'.format(e))
      return []


    if isinstance(sqlCommand, SQL_Select):
      self.sqlFireCommand = SQLFireQuery()

      # transform parsed SQL components into firebase queries
      queries = self.sqlFireCommand.generate(sqlCommand, options=options)
      fireQueries = self.sqlFireCommand.firebase_queries(queries)
      filterQueries = self.sqlFireCommand.filter_queries(queries)

      # execute firebase queries for each collection
      documents = self.sqlFireCommand.execute(client, fireQueries)

      # execute filter queries for each collection
      filterDocuments = self.sqlFireCommand.filter_documents(documents, filterQueries)

      # post-processing join of collections if needed
      selectDocs = self.sqlFireCommand.post_process(filterDocuments)

      # aggregation docs if function existed
      aggDocs = self.sqlFireCommand.aggregation(selectDocs)

      return aggDocs

    elif isinstance(sqlCommand, SQL_Insert):
      self.sqlFireCommand = SQLFireInsert()

      if self.sqlFireCommand.generate(sqlCommand, options=options):
        document = self.sqlFireCommand.build()
        insertedDoc = self.sqlFireCommand.execute(client, document)
        return [insertedDoc]
      else:
        return []

    elif isinstance(sqlCommand, SQL_Update):
      self.sqlFireCommand = SQLFireUpdate()

      # transform parsed SQL components into firebase queries
      queries = self.sqlFireCommand.generate(sqlCommand, options=options)
      fireQueries = self.sqlFireCommand.firebase_queries(queries)
      filterQueries = self.sqlFireCommand.filter_queries(queries)

      # execute firebase queries for each collection
      documents = self.sqlFireCommand.execute(client, fireQueries)

      # execute filter queries for each collection
      filterDocuments = self.sqlFireCommand.filter_documents(documents, filterQueries)

      # post-processing update of collections if needed
      updatedDocs = self.sqlFireCommand.update_execute(client, filterDocuments)
      return updatedDocs 

    elif isinstance(sqlCommand, SQL_Delete):
      self.sqlFireCommand = SQLFireDelete()

      # transform parsed SQL components into firebase queries
      queries = self.sqlFireCommand.generate(sqlCommand, options=options)
      fireQueries = self.sqlFireCommand.firebase_queries(queries)
      filterQueries = self.sqlFireCommand.filter_queries(queries)

      # execute firebase queries for each collection
      documents = self.sqlFireCommand.execute(client, fireQueries)

      # execute filter queries for each collection
      filterDocuments = self.sqlFireCommand.filter_documents(documents, filterQueries)

      # post-processing delete of collections if needed
      deletedDocs = self.sqlFireCommand.delete_execute(client, filterDocuments)
      return deletedDocs 
