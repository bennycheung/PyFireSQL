from abc import ABC, abstractmethod
from typing import Any, List, Dict


class FireSQLAbstractClient(ABC):
  """
  FireSQLAbstractClient is an abstract base class which defines
  the interface to the Firebase connection.

  It specifies the methods that query and retrieve the collection documents.
  """

  @property
  @abstractmethod
  def client(self):
    pass

  @abstractmethod
  def get_collection_ref(self, collectionName: str): 
    pass

  @abstractmethod
  def query_document_by_where_tuples(self, collectionName: str, queries: List) -> Dict:
    pass

  @abstractmethod
  def get_collection_document(self, collectionName: str, docId: str) -> Dict:
    pass

  @abstractmethod
  def get_collection_documents(self, collectionName: str) -> Dict:
    pass

  @abstractmethod
  def generate_collection_document_id(self, collectionName: str):
    pass

  @abstractmethod
  def set_collection_document(self, collectionName: str, docId: str, document: Dict):
    pass

  @abstractmethod
  def update_collection_document(self, collectionName: str, docId: str, document: Dict):
    pass

  @abstractmethod
  def delete_collection_document(self, collectionName: str, docId: str):
    pass



class FireSQLClient(FireSQLAbstractClient):
  """
  FireSQLClient is an implementation of the abstract Firebase connection class.

  It complies with the methods that query and retrieve the collection documents.
  """

  def __init__(self, firebaseClient: Any):
    self.firebaseClient = firebaseClient

  @property
  def client(self):
    return self.firebaseClient

  def get_collection_ref(self, collectionName: str): 
    return self.client.get_collection_ref(collectionName)

  def query_document_by_where_tuples(self, collectionName: str, queries: List) -> Dict:
    collectionRef = self.get_collection_ref(collectionName)
    return self.client.query_document_by_where_tuples(collectionRef, queries)
  
  def get_collection_document(self, collectionName: str, docId: str) -> Dict:
    collectionRef = self.get_collection_ref(collectionName)
    return self.client.get_document(collectionRef)

  def get_collection_documents(self, collectionName: str) -> Dict:
    collectionRef = self.get_collection_ref(collectionName)
    return self.client.get_collection_documents(collectionRef)

  def generate_collection_document_id(self, collectionName: str):
    collectionRef = self.get_collection_ref(collectionName)
    return self.client.generate_document_id(collectionRef)

  def set_collection_document(self, collectionName: str, docId: str, document: Dict):
    collectionRef = self.get_collection_ref(collectionName)
    return self.client.set_document(collectionRef, docId, document)

  def update_collection_document(self, collectionName: str, docId: str, document: Dict):
    collectionRef = self.get_collection_ref(collectionName)
    return self.client.update_document(collectionRef, docId, document)

  def delete_collection_document(self, collectionName: str, docId: str):
    collectionRef = self.get_collection_ref(collectionName)
    return self.client.delete_document(collectionRef, docId)
