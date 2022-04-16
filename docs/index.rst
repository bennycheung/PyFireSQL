.. PyFireSQL documentation master file, created by
   sphinx-quickstart on Fri Apr 15 08:13:23 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyFireSQL's documentation!
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Overview
   :hidden:

   parser
   future

.. toctree::
   :maxdepth: 2
   :caption: Tutorials & Guides
   :hidden:

   programming_interface
   query_script


.. toctree::
   :maxdepth: 2
   :caption: Reference
   :hidden:

   classes
   references

What is PyFireSQL
-----------------
PyFireSQL is a SQL-like programming interface to query Cloud Firestore collections using Python.
Cloud Firestore is a NoSQL, document-oriented database.
Unlike a SQL database, there are no tables or rows.
Instead, you store data in documents, which are organized into collections.

There is no formal query language to Cloud Firestore - NoSQL collection/document structure.
For many instances, we need to use the useful but clunky Firestore UI
to navigate, scroll and filter through the endless records. With the UI,
we have no way to extract the found documents.
Even though we attempted to extract and update by writing a unique program for the specific task,
we felt many scripts are almost the same that something must be done to limit the endless program writing.
What if we can use SQL-like statements to perform the data extraction, which is both formal and reusable?
- This idea will be the motivation for the FireSQL language!

Even though we see no relational data model of (table, row, column),
we can easily see the equivalent between table -> collection,  row -> document and column -> field
in the Firestore data model. The SQL-like statement can be transformed accordingly.

Install PyFireSQL
-----------------

.. code:: bash

   $ pip install pyfiresql

To install from [PyFireSQL source](https://github.com/bennycheung/PyFireSQL), checkout the project

.. code:: bash

   cd PyFireSQL
   # install require packages
   pip install -r requirements.txt
   # install (optional) development require packages
   pip install -r requirements_dev.txt

   python setup.py install


Programming Interface
---------------------

In PyFireSQL, we offer a simple programming interface to parse and execute firebase SQL.
Please consult [Firebase Admin SDK Documentation](https://firebase.google.com/docs/admin/setup) to generate the project's service account `credentials.json` file.

.. code:: python

   from firesql.firebase import FirebaseClient
   from firesql.sql import FireSQL

   # make connection to Cloud Firestore
   client = FirebaseClient()
   client.connect(credentials_json='credentials.json')

   # query via the FireSQL interface - the results are in list of docs (Dict)
   query = "SELECT * FROM Users WHERE state = 'ACTIVE'"
   fireSQL = FireSQL()
   docs = fireSQL.sql(client, query)


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
