## UPDATE Statement
The UPDATE statement is used to modify the existing documents in a collection.

----------------

### UPDATE Syntax

```sql
UPDATE collection_name
SET field1 = value1, field2 = value2, ...
WHERE condition;
```

> Note: Be careful when updating documents in a collection! Notice the WHERE clause in the UPDATE statement.
> The WHERE clause specifies which document(s) that should be updated. If we omit the WHERE clause, all documents in the collection will be updated!

### UPDATE Examples
The following UPDATE statement updates the user with email "btscheung+twotwo@gmail.com" to state "ACTIVE" in the "Users" collection:

```sql
UPDATE Users
SET
  state = 'ACTIVE'
WHERE
  email = 'btscheung+twotwo@gmail.com'
```

If we want to update with a field that takes complex data type, e.g. array or map, we must use "JSON()" data enclosure to encode the data.

```sql
UPDATE Users
  SET
    state = 'INACTIVE',
    groups = JSON(["TeamA", "TeamB"])
  WHERE
    state = 'ACTIVE' AND
    email = 'btscheung+twotwo@gmail.com'
```
