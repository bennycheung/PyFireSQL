## INSERT INTO Statement
The INSERT INTO statement is used to insert new document in a collection.

--------------

### INSERT INTO Syntax
Specify both the column names and the values to be inserted:

```sql
INSERT INTO collection_name (field1, field2, field3, ...)
VALUES (value1, value2, value3, ...);
```

### INSERT INTO Examples
The following SQL statement inserts a new document in the `Users` collection

```sql
INSERT INTO Users
    ( email, name, vaccination )
  VALUES
    ( 'btscheung+test1@gmail.com', 'Benny TwoTwo', NULL )
```

Since we are dealing with Firestore as a document structure without a schema,
we can insert all the key pairs from a JSON map into the collection.

For example, the following insert statement - column specification uses `*` to indicate all fields.
We are inserting a list of
`email`, `firstName`, `lastName`, `groups` (as array), `roles` (as array), `vaccination`, `access` (as map).

```
INSERT INTO Companies/bennycorp/Users
    ( * )
  VALUES (
    JSON(
      {
        "email": "btscheung+twotwo@gmail.com",
        "name": "Benny TwoTwo",
        "groups": [],
        "roles": [
            "ADMIN"
        ],
        "vaccination": null,
        "access": {
          "hasAccess": true
        }
      }
    )
  )
```
