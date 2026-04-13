select db.db_name,
       format(max(cast(mp_plotvalue as decimal(10,2))),2) 
 from sp_database db, sp_metricplot mp 
where db.db_id = mp.sp_database_db_id
  and mp.mp_metricname = 'DISK' 
  and mp.mp_metricAcronym = 'PERM' 
  and mp.mp_instance = 1
group by db.db_name;
