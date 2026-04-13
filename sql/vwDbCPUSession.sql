create or replace view vwDbCPUSession as
select mp_id cpu_id,
       mp_metricname cpu_metric,
       mp_metricacronym cpu_acronym,
       mp_instance cpu_instance,
       mp_plotdate cpu_date,
       mp_plotvalue cpu_value,
       sp_database_db_id cpu_database
  from sp_metricplot
 where mp_metricname = 'CPU'
   and mp_metricacronym = 'CPU'
 order by mp_id;

comment on view vwDbCPUSession is 'CPU and Active Sessions by database';

comment on column vwDbCPUSession.cpu_metric is 'CPU and Active Sessions Collection category';
comment on column vwDbCPUSession.cpu_acronym is 'CPU and Active Sessions Collection sub-category';
comment on column vwDbCPUSession.cpu_instance is 'CPU and Active Sessions Database Instance';
comment on column vwDbCPUSession.cpu_date is 'CPU and Active Sessions Collection point in time';
comment on column vwDbCPUSession.cpu_value is 'CPU and Active Sessions Collection data metric value';
comment on column vwDbCPUSession.cpu_database is 'CPU and Active Sessions associated to the collection';

