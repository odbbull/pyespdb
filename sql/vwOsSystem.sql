create or replace view vwOsSystem as
select mp_id oss_id,
       mp_metricname oss_metric,
       mp_metricacronym oss_acronym,
       mp_instance oss_instance,
       mp_plotdate oss_date,
       mp_plotvalue oss_value,
       sp_database_db_id oss_database
  from sp_metricplot
 where mp_metricname = 'OS'
   and mp_metricacronym = 'OSSYS'
 order by mp_id;

comment on table vwOsSystem is 'Operating System Metrics [OS System] by database';

comment on column vwOsSystem.oss_metric is 'Operating System Metrics [OS System] category';
comment on column vwOsSystem.oss_acronym is 'Operating System Metrics [OS System] Collection sub-category';
comment on column vwOsSystem.oss_instance is 'Operating System Metrics [OS System] Database Instance';
comment on column vwOsSystem.oss_date is 'Operating System Metrics [OS System] Collection point in time';
comment on column vwOsSystem.oss_value is 'Operating System Metrics [OS System] Collection data metric value';
comment on column vwOsSystem.oss_database is 'Operating System Metrics [OS System] associated to the collection';

