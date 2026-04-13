select cast(mp_plotvalue as decimal(10,2)) from sp_metricplot where mp_metricname = 'CPU' and mp_metricacronym='CPU' and mp_instance = 1 and sp_database_db_id = 359;
