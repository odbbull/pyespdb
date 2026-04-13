select vg_dbname, 
       vg_subdivision, 
       vg_dispYear, 
       vg_dispquarter,
       ms_instance,
       ms_avgvalue,
       ms_maxvalue   
  from vg_dbretirement,
       sp_database,
       sp_dbmetric_summ 
 where vg_dbname = db_name
   and db_id = sp_database_db_id
   and ms_metric = 'CPU'
   and ms_acronym = 'CPU'
 order by vg_dispYear, vg_dispquarter;
