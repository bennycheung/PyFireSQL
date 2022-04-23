## DELETE Statement
The DELETE statement is used to delete existing documents in a collection.

--------------
### DELETE Syntax

```sql
DELETE FROM table_name
WHERE condition;
```

> Note: Be careful when deleting documents in a collection!
> Notice the WHERE clause in the DELETE statement.
> The WHERE clause specifies which document(s) should be deleted. If you omit the WHERE clause, all documents in the collection will be deleted!

### DELETE Examples
The following DELETE statement deletes the user with email "btscheung+twotwo@gmail.com" from the "Users" collection:

```sql
DELETE
  FROM Users
  WHERE 
    email = 'btscheung+twotwo@gmail.com'
```
