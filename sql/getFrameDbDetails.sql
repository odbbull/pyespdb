select fr_name, fr_model, db_name, ms_metric, ms_acronym, ms_avgvalue, ms_maxvalue
  from sp_exaframe,
       sp_host,
       sp_database,
       sp_dbmetric_summ
 where fr_name = 'dc1sdeexa2'
   and fr_id = sp_exaframe_fr_id
   and hs_id = sp_host_hs_id
   and db_id = sp_database_db_id
   and ms_metric = 'CPU'
   and ms_acronym = 'CPU'
 order by db_name, ms_metric, ms_acronym
;
