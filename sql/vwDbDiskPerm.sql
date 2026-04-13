create or replace view vwDbDiskPerm as
select mp_id stp_id,
       mp_metricname stp_metric,
       mp_metricacronym stp_acronym,
       mp_instance stp_instance,
       mp_plotdate stp_date,
       mp_plotvalue stp_value,
       sp_database_db_id stp_database
  from sp_metricplot
 where mp_metricname = 'DISK'
   and mp_metricacronym = 'PERM'
 order by mp_id;

comment on view vwDbDiskPerm is 'Storage size for Database Files by database';

comment on column vwDbDiskPerm.stp_metric is 'Storage size for Database Files category';
comment on column vwDbDiskPerm.stp_acronym is 'Storage size for Database Files Collection sub-category';
comment on column vwDbDiskPerm.stp_instance is 'Storage size for Database Files Database Instance';
comment on column vwDbDiskPerm.stp_date is 'Storage size for Database Files Collection point in time';
comment on column vwDbDiskPerm.stp_value is 'Storage size for Database Files Collection data metric value';
comment on column vwDbDiskPerm.stp_database is 'Storage size for Database Files associated to the collection';

