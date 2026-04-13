select a.mp_plotdate
  from sp_metricplot a
 where a.sp_database_db_id = 397
   and a.mp_instance = 2
   and a.mp_metricName = 'CPU'
   and a.mp_metricAcronym = 'CPU';
