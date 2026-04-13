select distinct vg_dbname, 
       vg_dispYear, 
       vg_dispquarter,
       format(cast(a.ms_avgvalue as decimal(8,2)),2) "Inst1 Avg RMBPS",
       format(cast(a.ms_maxvalue as decimal(8,2)),2) "Inst1 Max RMBPS",
       format(cast(b.ms_avgvalue as decimal(8,2)),2) "Inst2 Avg RMBPS",
       format(cast(b.ms_maxvalue as decimal(8,2)),2) "Inst2 Max RMBPS"
  from vg_dbretirement,
       sp_database,
       sp_dbmetric_summ a,
       sp_dbmetric_summ b
 where vg_dbname = db_name
   and db_id = a.sp_database_db_id
   and a.ms_metric = 'MBPS'
   and a.ms_acronym = 'RBYTES'
   and a.ms_instance = 1
   and db_id = b.sp_database_db_id
   and b.ms_metric = 'MBPS'
   and b.ms_acronym = 'RBYTES'
   and b.ms_instance = 2
   and a.sp_database_db_id = b.sp_database_db_id
 order by format(cast(a.ms_maxvalue as decimal(8,2)),2);
