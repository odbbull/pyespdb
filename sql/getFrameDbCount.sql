select db_name
  from sp_database 
 where substr(db_name,1,3) in
    (select substr(db_name,1,3)
      from sp_database
     where substr(db_name,4,3) = upper('PRD'));
