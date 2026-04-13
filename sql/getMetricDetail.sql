SET @metric = 'MBPS';
SET @acronym = 'RBYTES';
SET @instance = 2;

select metr_instance, 
       metr_metricdate, 
       metr_metricvalue   
  from sp_dbmetric  
 where metr_metric = @metric
   and metr_acronym = @acronym
   and metr_instance = @instance
   and sp_database_db_id = 398  
 order by 1, 2;
