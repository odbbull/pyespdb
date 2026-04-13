select db_name,
       max(a.ms_maxvalue) "MBPS",
       max(b.ms_maxvalue) "CPU"
  from sp_dbmetric_summ a,
       sp_dbmetric_summ b,
       sp_database 
 where a.ms_maxvalue < 500    
   and a.ms_metric = 'MBPS' 
   and a.ms_acronym = 'RBYTES' 
   and a.sp_database_db_id = db_id
   and b.ms_maxvalue < 10
   and b.ms_metric = 'CPU'
   and b.ms_acronym = 'CPU'
   and b.sp_database_db_id = db_id
   and a.sp_database_db_id = b.sp_database_db_id
   and sp_collection_coll_id = 2
 group by db_name;
