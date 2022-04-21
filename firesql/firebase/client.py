# pip install firebase-admin
# pip install google-cloud-firestore
# generate a project private key JSON file
#
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth
from firebase_admin import storage
import datetime
import re
import json
import os
import importlib


class FirebaseClient:
  DATETIME_FORMAT = "%Y-%m-%d %H:%M:%SZ"
  DATETIME_FORMAT_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}Z$')


  def __init__(self):
    self.db = None
    self.auth = None
    self.bucket = None
    self.emulator = False


  def init_app(self, app):
    self.connect(
		  app.config['FIREBASE_PROJECT_ID'],
		  app.config['FIREBASE_CREDENTIAL']
	  )


  def is_connected(self):
    return self.db != None


  # call this to use emaultor support before connecting to firebase components
  def use_emulator(self, host='localhost', auth_port=9099, firestore_port=8088, storage_port=9199, functions_port=5001):
    self.emulator = True
    self.emulator_host = host
    self.emulators = {
      "auth": {
        "port": auth_port
      },
      "functions": {
        "port": functions_port
      },
      "firestore": {
        "port": firestore_port
      },
      "storage": {
        "port": storage_port,
      }
    }
    emulator_firestore_host = "{}:{}".format(host, firestore_port)
    emulator_firebase_auth_host = "{}:{}".format(host, auth_port)
    emulator_storage_host = "{}:{}".format(host, storage_port)

    # Setting the environment variables will make Admin SDK using emuators
    os.environ["FIRESTORE_EMULATOR_HOST"]=emulator_firestore_host
    os.environ["FIREBASE_AUTH_EMULATOR_HOST"]=emulator_firebase_auth_host
    os.environ["FIREBASE_STORAGE_EMULATOR_HOST"]=emulator_storage_host


  def connect(self, credentials_json, name='', config=None):
    cred = credentials.Certificate(credentials_json)

    if name == '':
      firebase_admin.initialize_app(cred, config)
      self.db = firestore.client(app=firebase_admin.get_app())
      self.auth = auth.Client(app=firebase_admin.get_app())
    else:
      # for multiple initialization with a different app name
      firebase_admin.initialize_app(cred, config, name=name)
      self.db = firestore.client(app=firebase_admin.get_app(name=name))
      self.auth = auth.Client(app=firebase_admin.get_app(name=name))

    if config:
      self.bucket = storage.bucket(config['storageBucket'])


  def get_user_by_email(self, email):
    user = self.auth.get_user_by_email(email.lower())
    return user


  def get_user_custom_token(self, email):
    # Since the Python Admin SDK cannot directly getting a user's access token,
    # we need to create a new Firebase custom token (JWT).
    # Later, we can the client signInWithCustomToken() methods to exchange with a access token.
    user = self.auth.get_user_by_email(email.lower())
    if user:
      uid = user.uid
      custom_token = self.auth.create_custom_token(uid)
      return custom_token
    return None


  def get_collection_ref(self, collection_id):
    return self.db.collection(u'{}'.format(collection_id))


  def get_document_ref(self, collection_ref, document_id):
    return collection_ref.document(document_id)


  def get_collection_documents(self, collection_ref):
    results = {}
    for doc in collection_ref.stream():
      results[doc.id] = doc.to_dict()
    return results


  def get_recursive_document(self, collection_ref, document_id):
      doc = collection_ref.document(document_id).get()
      if doc != None:
        result = doc.to_dict()
        # get document's collections into "collections" dict
        result["collections"] = {}
        collections = collection_ref.document(document_id).collections()
        for collection in collections:
            result["collections"][collection.id] = {}
            # get collection's documents into corresponding collection dict
            for cdoc in collection.stream():
                result["collections"][collection.id][cdoc.id] = self.get_recursive_document(collection, cdoc.id)
        return result
      else:
        return {}


  def get_document(self, collection_ref, document_id):
    doc_ref = self.get_document_ref(collection_ref, document_id)
    if (doc_ref):
      return doc_ref.get().to_dict()
    else:
      return {}


  def set_collection_documents(self, collection_ref, documents):
    # save document collections 
    for (doc_id, doc) in documents.items():
       self.set_document(collection_ref, doc_id, doc)


  def set_recursive_document(self, collection_ref, document_id, document):
      doc_ref = self.get_document_ref(collection_ref, document_id)
      subcollections = document["collections"] 

      # save document collections recursively
      for (collection_id, collection) in subcollections.items():
        subcollection_ref = doc_ref.collection(collection_id)
        for (cdoc_id, cdoc) in collection.items():
          self.set_recursive_document(subcollection_ref, cdoc_id, cdoc)

      # since the collections are saved, remove "collections" in the document field      
      del document["collections"]
      self.set_document(collection_ref, document_id, document)
      
      # restore "collections" in the given document
      document["collections"] = subcollections


  def generate_document_id(self, collection_ref):
    return collection_ref.document().id


  def set_document(self, collection_ref, document_id, document):
    doc_ref = self.get_document_ref(collection_ref, document_id)
    doc_ref.set(document)
    return doc_ref


  def update_document(self, collection_ref, document_id, document):
    doc_ref = self.get_document_ref(collection_ref, document_id)
    doc_ref.set(document, merge=True)
    return doc_ref


  def delete_document(self, collection_ref, document_id):
    doc_ref = self.get_document_ref(collection_ref, document_id)
    if (doc_ref):
      doc_ref.delete()


  def query_document(self, collection_ref, attribute, op, value):
    query_ref = collection_ref.where(attribute, op, value)
    results = {}
    for doc in query_ref.stream():
      results[doc.id] = doc.to_dict()
    return results


  def query_document_by_where_tuples(self, collection_ref, whereTuples):
    # whereTuples is [(key, operator, value), ...]
    # if key is 'docid', do special document id processing
    results = {}
    for whereTuple in whereTuples:
      (key, operator, value) = whereTuple
      if key == 'docid':
        if operator == '==':
          doc = self.get_document(collection_ref, value)
          if doc:
            results[value] = doc
        elif operator == 'in':
          if isinstance(value, list):
            for v in value:
              doc = self.get_document(collection_ref, v)
              if doc:
                results[v] = doc
        return results

    # otherwise, preform the where queries
    query_ref = collection_ref
    for whereTuple in whereTuples:
      (key, operator, value) = whereTuple
      query_ref = query_ref.where(key, operator, value)
    for doc in query_ref.stream():
      results[doc.id] = doc.to_dict()
    return results


  def document_to_json(self, document, indent=2):
    def _convert_datetime(o):
      if isinstance(o, datetime.datetime):
        return o.strftime(FirebaseClient.DATETIME_FORMAT)

    json_str = json.dumps(document, indent=indent, default=_convert_datetime)
    return json_str


  def json_to_document(self, json_str):
    def _datetime_parser(dct):
      for k, v in dct.items():
          if isinstance(v, str) and FirebaseClient.DATETIME_FORMAT_REGEX.match(v):
              dct[k] = datetime.datetime.strptime(v, FirebaseClient.DATETIME_FORMAT)
      return dct

    document = json.loads(json_str, object_hook=_datetime_parser)
    return document
  

  def generate_password_reset_link(self, email):
    password_reset_link = self.auth.generate_password_reset_link(email.lower())
    if password_reset_link:
      return password_reset_link
    return None
