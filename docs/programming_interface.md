# Programming Interface
In PyFireSQL, we offer a simple programming interface to parse and execute firebase SQL.
Please consult [Firebase Admin SDK Documentation](https://firebase.google.com/docs/admin/setup) to generate the project's service account `credentials.json` file.

---------

```python
from firesql.firebase import FirebaseClient
from firesql.sql.sql_fire_client import FireSQLClient
from firesql.sql import FireSQL

# make connection to Cloud Firestore
client = FirebaseClient()
client.connect(credentials_json='credentials.json')
# wrapped as FireSQL client interface
sqlClient = FireSQLClient(client)

# query via the FireSQL interface - the results are in list of docs (Dict)
query = "SELECT * FROM Users WHERE state = 'ACTIVE'"
fireSQL = FireSQL()
docs = fireSQL.execute(sqlClient, query)
```

After `fireSQL.execute()` query completed, the results are a list of docs (as Dict) that satisfied the query.
Then we can pass the list of docs to render into any output format, in our case, the `DocPrinter` object can output `csv` or `json` with the select fields.

```python
from firesql.sql.doc_printer import DocPrinter

docPrinter = DocPrinter()
if format == 'csv':
  docPrinter.printCSV(docs, fireSQL.select_fields())
else:
  docPrinter.printJSON(docs, fireSQL.select_fields())
```

For further post-processing, we can use Pandas's Dataframe to perform any data analysis, grouping, sorting and calculations. The list of docs (as Dict) can be directly imported into Dataframe! very convenience.

```python
import pandas as pd

df = pd.DataFrame(docs)
```
