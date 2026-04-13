select db_id,
       db_name "Database",
       db_host_model "Exa Model",
       mp_metricAcronym,
       format(max(cast(a.mp_plotvalue as decimal(12.2))),2) "DB Size"
  from sp_metricplot a,
       sp_database b
 where a.mp_metricname = 'DISK' 
   and a.sp_database_db_id = b.db_id
   and b.sp_collection_coll_id = 2
 group by db_id, db_name, db_host_model, mp_metricAcronym
 order by db_name, mp_metricAcronym;
