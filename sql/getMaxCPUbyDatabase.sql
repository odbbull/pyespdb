select db.db_name,
       max(cast(mp.mp_plotvalue as decimal(10,2)))   
 from sp_database db, sp_metricplot mp
where db.db_id = mp.sp_database_db_id
  and mp.mp_metricname = 'CPU' 
  and mp.mp_metricAcronym = 'CPU' 
group by db.db_name;
