create or replace view vwOsIdle as
select mp_id osi_id,
       mp_metricname osi_metric,
       mp_metricacronym osi_acronym,
       mp_instance osi_instance,
       mp_plotdate osi_date,
       mp_plotvalue osi_value,
       sp_database_db_id osi_database
  from sp_metricplot
 where mp_metricname = 'OS'
   and mp_metricacronym = 'IDLE'
 order by mp_id;

comment on table vwOsIdle is 'Operating System Metrics [OS Idle] by database';

comment on column vwOsIdle.osi_metric is 'Operating System Metrics [OS Idle] category';
comment on column vwOsIdle.osi_acronym is 'Operating System Metrics [OS Idle] Collection sub-category';
comment on column vwOsIdle.osi_instance is 'Operating System Metrics [OS Idle] Database Instance';
comment on column vwOsIdle.osi_date is 'Operating System Metrics [OS Idle] Collection point in time';
comment on column vwOsIdle.osi_value is 'Operating System Metrics [OS Idle] Collection data metric value';
comment on column vwOsIdle.osi_database is 'Operating System Metrics [OS Idle] associated to the collection';

