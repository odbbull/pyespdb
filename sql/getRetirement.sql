select vg_dbName, 
       vg_dispQuarter "qtr", 
       vg_dispYear "yr",  
       db_collection_host,
       db_host_model,
       vg_disposition,
       substr(vg_application,1,30) "App"
  from vg_dbretirement, 
       sp_database
 where vg_dbName = db_name  
 order by vg_dispyear, vg_dispquarter
