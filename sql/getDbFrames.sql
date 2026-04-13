select fr_name, fr_location, fr_model, count(*)
  from sp_exaframe, sp_host, sp_database
 where fr_id = sp_exaframe_fr_id
   and hs_id = sp_host_hs_id
 group by fr_name, fr_location, fr_model
 order by fr_location, fr_model;
