create or replace view vwDbWriteIOPS as
select mp_id dio_id,
       mp_metricname dio_metric,
       mp_metricacronym dio_acronym,
       mp_instance dio_instance,
       mp_plotdate dio_date,
       mp_plotvalue dio_value,
       sp_database_db_id dio_database
  from sp_metricplot
 where mp_metricname = 'IOPS'
   and mp_metricacronym = 'WREQS'
 order by mp_id;

comment on table vwDbWriteIOPS is 'Storage Write IO per Second (IOPS) by database';

comment on column vwDbWriteIOPS.dio_metric is 'Storage Write IO per Second (IOPS) category';
comment on column vwDbWriteIOPS.dio_acronym is 'Storage Write IO per Second (IOPS) Collection sub-category';
comment on column vwDbWriteIOPS.dio_instance is 'Storage Write IO per Second (IOPS) Database Instance';
comment on column vwDbWriteIOPS.dio_date is 'Storage Write IO per Second (IOPS) Collection point in time';
comment on column vwDbWriteIOPS.dio_value is 'Storage Write IO per Second (IOPS) Collection data metric value';
comment on column vwDbWriteIOPS.dio_database is 'Storage Write IO per Second (IOPS) associated to the collection';

