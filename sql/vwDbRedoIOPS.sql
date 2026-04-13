create or replace view vwDbRedoIOPS as
select mp_id dio_id,
       mp_metricname dio_metric,
       mp_metricacronym dio_acronym,
       mp_instance dio_instance,
       mp_plotdate dio_date,
       mp_plotvalue dio_value,
       sp_database_db_id dio_database
  from sp_metricplot
 where mp_metricname = 'IOPS'
   and mp_metricacronym = 'WREDO'
 order by mp_id;

comment on table vwDbRedoIOPS is 'Storage Redo Log IO per Second (IOPS) by database';

comment on column vwDbRedoIOPS.dio_metric is 'Storage Redo Log IO per Second (IOPS) category';
comment on column vwDbRedoIOPS.dio_acronym is 'Storage Redo Log IO per Second (IOPS) Collection sub-category';
comment on column vwDbRedoIOPS.dio_instance is 'Storage Redo Log IO per Second (IOPS) Database Instance';
comment on column vwDbRedoIOPS.dio_date is 'Storage Redo Log IO per Second (IOPS) Collection point in time';
comment on column vwDbRedoIOPS.dio_value is 'Storage Redo Log IO per Second (IOPS) Collection data metric value';
comment on column vwDbRedoIOPS.dio_database is 'Storage Redo Log IO per Second (IOPS) associated to the collection';

