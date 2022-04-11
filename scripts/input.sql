SELECT u.email, u.state, b.date, b.state
  FROM
    Companies/bennycorp/Users as u JOIN Companies/bennycorp/Bookings as b
    ON u.email = b.email
  WHERE 
      u.state = 'ACTIVE' AND
      u.email LIKE '%benny%' AND
      b.state IN ('CHECKED_IN', 'CHECKED_OUT') AND
      b.date >= '2022-03-18T04:00:00'