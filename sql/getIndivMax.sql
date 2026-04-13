select db_id,
       db_name "Database",
       db_host_model "Exa Model",
       substr(vg_application,1,30) "Application",
       vg_dispQuarter "Qtr",
       vg_dispYear "Year",
       format(max(cast(a.ms_maxvalue as decimal(12,2))),2) "MBPS",
       format(max(cast(b.ms_maxvalue as decimal(12,2))),2) "CPU",
       format(max(cast(c.ms_maxvalue as decimal(12.2))),2) "DB Size"
  from sp_dbmetric_summ a,
       sp_dbmetric_summ b,
       sp_dbmetric_summ c,
       sp_database,
       vg_dbretirement
 where a.ms_metric = 'MBPS' 
   and a.ms_acronym = 'RBYTES' 
   and a.sp_database_db_id in (398)
   and a.sp_database_db_id = db_id
   and b.ms_metric = 'CPU'
   and b.ms_acronym = 'CPU'
   and b.sp_database_db_id in (398)
   and b.sp_database_db_id = db_id
   and c.ms_metric = 'DISK'
   and c.ms_acronym = 'PERM'
   and c.sp_database_db_id in (398)
   and c.sp_database_db_id = db_id
   and a.sp_database_db_id = b.sp_database_db_id
   and a.sp_database_db_id = c.sp_database_db_id
   and b.sp_database_db_id = c.sp_database_db_id
   and sp_collection_coll_id = 4
   and db_name = vg_dbName
 group by db_id, db_name, db_host_model, vg_application, vg_dispQuarter, vg_dispYear
 order by db_id;
