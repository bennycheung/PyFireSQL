## SELECT Statement
The SELECT statement is used to select data from a database.

--------------------
### SELECT Syntax
```sql
SELECT field1, field2, ...
FROM collection_name
WHERE conditions
```

Here, field1, field2, ... are the field names of the collection to select data from.
If we want to select all the fields available in the collection, use the following syntax:

```sql
SELECT *
FROM collection_name
```

By using `lark` [EBNF-like grammar](https://github.com/bennycheung/PyFireSQL/blob/main/firesql/sql/grammar/firesql.lark),
we have encoded the core `SELECT` statement, which is subsequently transformed into Firestore collection queries to be executed.

- SELECT columns for collection field's projection
- FROM sub-clause for collections
- FROM/JOIN sub-clause for joining collections (restricted to 1 join)
- WHERE sub-clause with boolean algebra expression for each collection's queries on field values
  - boolean operators: AND (currently OR is not implemented)
  - operators: =, !=, >, <, <=, >=
  - container expressions: IN, NOT IN
  - array contains expressions: CONTAIN, ANY CONTAIN
  - filter expressions: LIKE, NOT LIKE
  - null expressions: IS NULL, IS NOT NULL
- Aggregation functions applied to the result set
  - COUNT for any field
  - SUM, AVG, MIN, MAX for numeric field

But the processor has the following limitations, which we can provide post-processing on the query results set.
- No ORDER BY sub-clause
- No GROUP BY/HAVING sub-clause
- No WINDOW sub-clause

### SELECT Examples
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

> The `*` will select all fields, boolean operator 'AND' to specify multiple query criteria.
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

> The `COUNT`, `MIN`, `MAX`, `SUM`, `AVG` are the aggregation functions computed against the result set.
> Only numeric field (e.g. `cost` here) is numeric to have a valid value for `MIN`, `MAX`, `SUM`, `AVG` computation.
```sql
SELECT COUNT(*), MIN(b.cost), MAX(b.cost), SUM(b.cost), AVG(b.cost)
  FROM
    Users as u JOIN Bookings as b
    ON u.email = b.email
  WHERE 
      u.state = 'ACTIVE' AND
      u.email LIKE '%benny%' AND
      b.state IN ('CHECKED_IN', 'CHECKED_OUT') AND
```
      

> See [firesql.lark](https://github.com/bennycheung/PyFireSQL/blob/main/firesql/sql/grammar/firesql.lark) for the FireSQL grammar specification.
