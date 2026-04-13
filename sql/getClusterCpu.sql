select db.db_name,
       mp1.mp_plotdate,
       cast(mp1.mp_plotvalue as decimal(10.2)) instance1,
       cast(mp2.mp_plotvalue as decimal(10.2)) instance2
  from sp_database db,
       sp_metricplot mp1,
       sp_metricplot mp2
 where db.db_id = mp1.sp_database_db_id
   and db.db_id = mp2.sp_database_db_id
   and mp1.mp_metricname = 'CPU'
   and mp1.mp_metricacronym = 'CPU'
   and mp1.mp_metricname = mp2.mp_metricname
   and mp1.mp_metricacronym = mp2.mp_metricacronym
   and mp1.mp_plotdate = mp2.mp_plotdate
   and mp1.mp_instance = 1
   and mp2.mp_instance = 2
   and db.db_id = 375;
