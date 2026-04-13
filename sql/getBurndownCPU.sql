select vg_dbname, 
       vg_subdivision, 
       vg_dispYear, 
       vg_dispquarter,
       ms_instance,
       cast(ms_avgvalue as decimal(6,2)) "avg cpu",
       cast(ms_maxvalue as decimal(6,2)) "max cpu"
  from vg_dbretirement,
       sp_database,
       sp_dbmetric_summ 
 where vg_dbname = db_name
   and db_id = sp_database_db_id
   and ms_metric = 'CPU'
   and ms_acronym = 'CPU'
 order by 7 asc;
