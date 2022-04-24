# PyFireSQL
PyFireSQL is a SQL-like programming interface to query [Cloud Firestore](https://firebase.google.com/products/firestore) collections using Python.

There is no formal query language to Cloud Firestore - NoSQL collection/document structure. For many instances, we need to use the useful but clunky Firestore UI to navigate, scroll and filter through the endless records. With the UI, we have no way to extract the found documents. Even though we attempted to extract and update by writing a unique program for the specific task, we felt many scripts are almost the same that something must be done to limit the endless program writing. What if we can use SQL-like statements to perform the data extraction, which is both formal and reusable? - This idea will be the motivation for the FireSQL language!

Even though we see no relational data model of (table, row, column), we can easily see the equivalent between table -> collection,  row -> document and column -> field in the Firestore data model. The SQL-like statement can be transformed accordingly.

## Quick links
- [Documentation @readthedocs](https://pyfiresql.readthedocs.io/)
- [FireSQL in Python blog post](https://bennycheung.github.io/firesql-in-python)

## How to install
To install PyFireSQL from PyPi,

```
pip install pyfiresql
```

To install from [PyFireSQL source](https://github.com/bennycheung/PyFireSQL), checkout the project
```sh
cd PyFireSQL
# install require packages
pip install -r requirements.txt
# install (optional) development require packages
pip install -r requirements_dev.txt

python setup.py install
```

## FireSQL Statements
The set of implemented SQL-like DML (Data Manipulation Language) statements are,

| FireSQL Statement | Description |
|---------------|-------------|
| SELECT | select documents from a collection
| INSERT | insert new document in a collection
| UPDATE | modify the existing documents in a collection
| DELETE | delete existing documents in a collection

Please read the details in the corresponding [FireSQL Documentation @readthedocs](https://pyfiresql.readthedocs.io/en/latest/).

> See `firesql/sql/grammar/firesql.lark` for the FireSQL grammar specification.

## FireSQL to Firebase Query
We provided a simple firebase SQL interface class that can be easily applied a SQL statement to fetch from Firebase collections.

### Programming Interface
In PyFireSQL, we offer a simple programming interface to parse and execute firebase SQL.

```python
from firesql.firebase import FirebaseClient
from firesql.sql import FireSQL

# make connection to Cloud Firestore
client = FirebaseClient()
client.connect(credentials_json='credentials.json')

# query via the FireSQL interface - the results are in list of docs (Dict)
query = "SELECT * FROM Users WHERE state = 'ACTIVE'"
fireSQL = FireSQL()
docs = fireSQL.execute(client, query)
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

### Query Script

In addition, we provide an interface script `firesql-query.py` to accept an FireSQL statement.

```
usage: firesql-query.py [-h] [-c CREDENTIALS] [-f FORMAT] [-i INPUT]
                        [-q QUERY]

optional arguments:
  -h, --help            show this help message and exit
  -c CREDENTIALS, --credentials CREDENTIALS
                        credentials JSON path
  -f FORMAT, --format FORMAT
                        output format (csv|json)
  -i INPUT, --input INPUT
                        FireSQL query input file (required)
  -q QUERY, --query QUERY
                        FireSQL query (required)
```
For example, finding all `ACTIVE` users from Users collection

```
python firesql-query.py -c credential.json \
  -q "SELECT docid, email, state FROM Users WHERE state IN ('ACTIVE')"
```
> `docid` is a special column name that is used to project the Firestore document ID.

The default query result is rendered in "csv" output format.

```
"docid","email","state"
"0r6YWowe9rW65yB1qTKsCe83cCm2","btscheung+real@gmail.com","ACTIVE"
"1utcUa9fdheOlrMe9GOCjrJ3wjh1","btscheung+bennycorp@gmail.com","ACTIVE"
"7CUJOqe6rlOTQuatc27EQGivZfn2","btscheung+twotwo@gmail.com","ACTIVE"
...
```

Alternatively, by specifying the `-f json` output format, the result will be,

```json
[
  {"docid": "0r6YWowe9rW65yB1qTKsCe83cCm2", "email": "btscheung+real@gmail.com", "state": "ACTIVE"},
  {"docid": "1utcUa9fdheOlrMe9GOCjrJ3wjh1", "email": "btscheung+bennycorp@gmail.com", "state": "ACTIVE"},
  {"docid": "7CUJOqe6rlOTQuatc27EQGivZfn2", "email": "btscheung+twotwo@gmail.com", "state": "ACTIVE"},
  ...
]
```
#### SQL Input File
For more complicated SQL, we can use `-i input.sql` to specify the SQL input file.

`input.sql` file:
```sql
SELECT u.email, u.state, b.date, b.state
  FROM
    Users as u JOIN Bookings as b
    ON u.email = b.email
  WHERE 
      u.state IN ('ACTIVE') and
      b.state IN ('CHECKED_IN', 'CHECKED_OUT') and
      b.date >= '2022-03-18T04:00:00'
```

By execute the input file

```
python firesql-query.py -c credentials.json -i input.sql
```

The result will be,
> NOTE: the column `state` from `Users` will be automatically disambiguated by appending the alias prefix `u_state`.

```
"email","u_state","date","state"
"btscheung+bennycorp@gmail.com","ACTIVE","2022-03-18T04:00:00","CHECKED_IN"
"btscheung+bennycorp@gmail.com","ACTIVE","2022-03-18T04:00:00","CHECKED_IN"
"btscheung+hill6@gmail.com","ACTIVE","2022-03-31T04:00:00","CHECKED_IN"
...
```

## Release
Create a source distribution and upload to PyPi

```
rm -rf dist
rm -rf build
python setup.py sdist
twine upload dist/*
```

## References
- Gabriele Tomassetti, [Parsing In Python: Tools And Libraries](https://tomassetti.me/parsing-in-python/)
- [Lark Documentation](https://lark-parser.readthedocs.io/en/latest/)
  - Repo: [lark-parser](https://github.com/lark-parser/lark)
