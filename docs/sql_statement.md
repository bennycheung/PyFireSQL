## FireSQL Statements
FireSQL supports the following SQL-like statements.

---------------------
The set of implemented SQL-like DML (Data Manipulation Language) statements are,

| FireSQL Statement | Description |
|---------------|-------------|
| SELECT | select documents from a collection
| INSERT | insert new document in a collection
| UPDATE | modify the existing documents in a collection
| DELETE | delete existing documents in a collection

Please read the details in the corresponding FireSQL statement sections. 

### Multiple Statements
The `FireSQL.execute()` function can take one or more FireSQL statements. Sequence of statements must be separated by semi-colon ';'.

For example,

```sql
INSERT INTO Users (email, name) VALUES ('btscheung+oneone@gmail.com', 'Benny OneOne');
INSERT INTO Users (email, name) VALUES ('btscheung+twotwo@gmail.com', 'Benny TwoTwo');
INSERT INTO Users (email, name) VALUES ('btscheung+threethree@gmail.com', 'Benny ThreeThree')

```

> - The last FireSQL statement's semi-colon is optional.
