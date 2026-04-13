create or replace view vwDbDiskUndo as
select mp_id stu_id,
       mp_metricname stu_metric,
       mp_metricacronym stu_acronym,
       mp_instance stu_instance,
       mp_plotdate stu_date,
       mp_plotvalue stu_value,
       sp_database_db_id stu_database
  from sp_metricplot
 where mp_metricname = 'DISK'
   and mp_metricacronym = 'UNDO'
 order by mp_id;

comment on view vwDbDiskUndo is 'Storage size for Undo Files by database';

comment on column vwDbDiskUndo.stu_metric is 'Storage size for Undo Files category';
comment on column vwDbDiskUndo.stu_acronym is 'Storage size for Undo Files Collection sub-category';
comment on column vwDbDiskUndo.stu_instance is 'Storage size for Undo Files Database Instance';
comment on column vwDbDiskUndo.stu_date is 'Storage size for Undo Files Collection point in time';
comment on column vwDbDiskUndo.stu_value is 'Storage size for Undo Files Collection data metric value';
comment on column vwDbDiskUndo.stu_database is 'Storage size for Undo Files associated to the collection';

