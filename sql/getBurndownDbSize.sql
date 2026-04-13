select vg_dbname, 
       vg_subdivision, 
       vg_dispYear, 
       vg_dispquarter,
       ms_instance,
       format(cast(ms_maxvalue as decimal(12,2)),2) "max size" 
  from vg_dbretirement,
       sp_database,
       sp_dbmetric_summ 
 where vg_dbname = db_name
   and db_id = sp_database_db_id
   and ms_metric = 'DISK'
   and ms_acronym = 'PERM'
 order by vg_dispYear, vg_dispquarter;
