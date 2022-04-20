SELECT docid, date, "visitor.email", ancestors, visitor
  FROM
    Companies/bennycorp/Bookings
  WHERE
    state IN ('CHECKED_IN', 'CHECKED_OUT') AND
    date >= '2022-03-18T04:00:00'

