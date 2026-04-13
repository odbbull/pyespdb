create or replace view vwDbDiskLog as
select mp_id stl_id,
       mp_metricname stl_metric,
       mp_metricacronym stl_acronym,
       mp_instance stl_instance,
       mp_plotdate stl_date,
       mp_plotvalue stl_value,
       sp_database_db_id stl_database
  from sp_metricplot
 where mp_metricname = 'DISK'
   and mp_metricacronym = 'LOG'
 order by mp_id;

comment on view vwDbDiskLog is 'Storage size for Redo Log by database';

comment on column vwDbDiskLog.stl_metric is 'Storage size for Redo Log category';
comment on column vwDbDiskLog.stl_acronym is 'Storage size for Redo Log Collection sub-category';
comment on column vwDbDiskLog.stl_instance is 'Storage size for Redo Log Database Instance';
comment on column vwDbDiskLog.stl_date is 'Storage size for Redo Log Collection point in time';
comment on column vwDbDiskLog.stl_value is 'Storage size for Redo Log Collection data metric value';
comment on column vwDbDiskLog.stl_database is 'Storage size for Redo Log associated to the collection';

