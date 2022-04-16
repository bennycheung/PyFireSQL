# Query Script

In addition, we provide an interface script `firesql-query.py` to accept an FireSQL statement.

-----------

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
