select db.db_id,
       db.db_name,
       date(mp1.mp_plotdate),
       mp1.mp_instance,
       avg(cast(mp1.mp_plotvalue as decimal(10.2))) sessions
  from sp_database db,
       sp_metricplot mp1
 where db.db_id = mp1.sp_database_db_id
   and mp1.mp_metricname = 'CPU'
   and mp1.mp_metricacronym = 'CPU'
 group by db.db_id, db.db_name, date(mp1.mp_plotdate), mp1.mp_instance
