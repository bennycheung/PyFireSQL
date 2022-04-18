# firesql-query.py
# Hive Firebase company query by where clauses
#
# USAGE
# For example, find all Bookings by email and at date, * means everything
# python firesql-query.py -m prod -c mlse -q "SELECT * FROM Bookings WHERE email = 'john_thurner@hotmail.com' AND date = '2022-03-18T00:00:00-04:00'"
# For example, find all Bookings by email and at date, only select fields for id,date,email
# python firesql-query.py -m prod -c mlse -q "SELECT id,date,email FROM Bookings WHERE email = 'john_thurner@hotmail.com' AND date = '2022-03-18T00:00:00-04:00'"
# For example, find all Bookings by email and at date, only select fields for id,date,email
# python firesql-query.py -m prod -c mlse -q "SELECT id,date,email FROM Bookings WHERE email = 'john_thurner@hotmail.com' AND date = '2022-03-18T00:00:00-04:00'"
#
# For example, find out all ACTIVE users, who actually made bookings that either were
# CHECKED_IN or CHECKED_OUT. This is essentially trying to find users who really used the system.
# The SQL query is specified in sqltest1.sql.
# python firesql-query.py -m dev -c bennycorp -i sqltest1.sql


# import the necessary packages
import argparse
from firesql.firebase import FirebaseClient

from firesql.sql.sql_fire_client import FireSQLClient
from firesql.sql import FireSQL, DocPrinter

if __name__ == "__main__":
  # construct the argument parser and parse the arguments
  ap = argparse.ArgumentParser()
  ap.add_argument("-c", "--credentials", type=str, default="../credentials/credentials.json",
    help="credentials JSON path")
  ap.add_argument("-f", "--format", type=str, default="csv",
    help="output format (csv|json)")
  ap.add_argument("-i", "--input", type=str, default="",
    help="FireSQL query input file (required)")
  ap.add_argument("-q", "--query", type=str, default="",
    help="FireSQL query (required)")
  args = vars(ap.parse_args())

  credentials = args["credentials"]
  format = args["format"].lower()
  input = args["input"]
  query = args["query"]

  if not query:
    if input:
      with open(file=input) as sql_file:
        query = sql_file.read()
  
  if not query:
    print("must specify query")
    exit(0)

  client = FirebaseClient()
  client.connect(credentials_json=credentials)
  sqlClient = FireSQLClient(client)

  fireSQL = FireSQL()
  docs = fireSQL.sql(sqlClient, query)

  if docs:
    docPrinter = DocPrinter()
    if format == 'csv':
      docPrinter.printCSV(docs, fireSQL.select_fields())
    else:
      docPrinter.printJSON(docs, fireSQL.select_fields())
  else:
    print("no record found!")
