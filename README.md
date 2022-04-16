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

## Just Enough SQL for FireSQL
To get going, we don't need the full SQL parser and transformer for the DML (Data Manipulation Language). We define ONLY the `SELECT` statement, just enough for Firestore collections query to serve our immediate needs.

By using [Lark](https://lark-parser.readthedocs.io/en/latest/) EBNF-like grammar, we have encoded the core `SELECT` clause, which can translate into Firestore collection queries.
- SELECT columns for collection field's projection
- FROM sub-clause for collections
- FROM/JOIN sub-clause for joining collections (restricted to 1 join)
- WHERE sub-clause with boolean algebra expression for each collection's queries on field values
  - boolean operators: AND (currently OR is not implemented)
  - operators: =, !=, >, <, <=, >=
  - container expressions: IN, NOT IN
  - array contains expressions: CONTAIN, ANY CONTAIN
  - filter expressions: LIKE, NOT LIKE
  - null expressions: IS NULL
- All keywords are case insensitive. All whitespaces are ignored.

But the processor has the following limitations:
- No ORDER BY sub-clause
- No GROUP BY/HAVING sub-clause
- No WINDOW sub-clause

For example, the following statements can be expressed,
> All keywords are case insensitive. All whitespaces are ignored by the parser.

> `docid` is a special field name to extract the selected document's Id
```sql
  SELECT docid, email, state
    FROM
      Users
    WHERE
      state = 'ACTIVE'
```

> The '*' will select all fields, boolean operator 'AND' to specify multiple query criteria.
```sql
  SELECT *
    FROM
      Users
    WHERE
      state IN ('ACTIVE') AND
      u.email LIKE '%benny%'
```

> The field-subfield can use the `"` to escape the field name with `.` in it.
```sql
  SELECT *
    FROM
      Users as u
    WHERE
      u.state IN ('ACTIVE') AND
      u."location.displayName" = 'Work From Home'
```

> The `JOIN` expression to join 2 collections together
```sql
SELECT u.email, u.state, b.date, b.state
  FROM
    Users as u JOIN Bookings as b
    ON u.email = b.email
  WHERE 
      u.state = 'ACTIVE' AND
      u.email LIKE '%benny%' AND
      b.state IN ('CHECKED_IN', 'CHECKED_OUT') AND
      b.date >= '2022-03-18T04:00:00'
```

> See `firesql/sql/grammar/firesql.lark` for the FireSQL grammar specification.

### Collection Path
The Firestore collection has a set of documents. Each document can be nested with more collections. Firestore identifies a collection by a path, looks like `Companies/bennycorp/Users` means `Companies` collection has a document `bennycorp`, which has `Users` collection.

If we want to query a nested collection, we can specify the collection name as a path.
The paths can be long but we can use `AS` keyword to define their alias names.

For example, the subcollection `Users` and `Bookings` are specified with `Companies/bennycorp` document.

```sql
SELECT u.email, u.state, b.date, b.state
  FROM
    Companies/bennycorp/Users as u JOIN Companies/bennycorp/Bookings as b
    ON u.email = b.email
  WHERE 
      u.state = 'ACTIVE' AND
      b.date >= '2022-03-18T04:00:00'
```

> Interesting Firestore Fact: collection path must have odd number of parts.

### DateTime Type
Consistent description of date-time is a big topic the we made a practical design choice.
We are using [ISO-8601](https://en.wikipedia.org/wiki/ISO_8601) to express the date-time as a string,
while Firestore stores the date-time as `Timestamp` data type in UTC.
For example,
- writing "March 18, 2022, at time 4 Hours in UTC" date-time string, is "2022-03-18T04:00:00".
- writing "March 18, 2022, at time 0 Hours in Toronto Time EDT (-4 hours)" date-time string, is "2022-03-18T00:00:00-04".

If in doubt, we are using the following to convert, match and render to the ISO-8601 string for date-time values.

```python
DATETIME_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATETIME_ISO_FORMAT_REGEX = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'
```

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
docs = fireSQL.sql(client, query)
```

After `fireSQL.sql()` query completed, the results are a list of docs (as Dict) that satisfied the query.
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

### Pattern Matching by LIKE
The SQL expression `LIKE` or `NOT LIKE` can be used for matching string data.

```sql
SELECT docid, email, state
  FROM
    Users
  WHERE
    state IN ('ACTIVE') AND
    email LIKE '%benny%'
```

After the Firebase query, the pattern matching is used as the filtering expression. The SQL processor supports pattern for:
- prefix match `pattern%`
- suffix match `%pattern`
- infix match `%pattern%`


## References
- Gabriele Tomassetti, [Parsing In Python: Tools And Libraries](https://tomassetti.me/parsing-in-python/)
- [Lark Documentation](https://lark-parser.readthedocs.io/en/latest/)
  - Repo: [lark-parser](https://github.com/lark-parser/lark)

