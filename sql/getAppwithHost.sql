select distinct db_name
  from sp_database, 
       sp_host, 
       sp_exaframe
 where sp_collection_coll_id > 1
   and sp_host_hs_id = hs_id    
   and sp_exaframe_fr_id = fr_id
   and fr_name = 'dc2gisexa2';
