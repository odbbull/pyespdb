create or replace view vwOsBusy as
select mp_id osb_id,
       mp_metricname osb_metric,
       mp_metricacronym osb_acronym,
       mp_instance osb_instance,
       mp_plotdate osb_date,
       mp_plotvalue osb_value,
       sp_database_db_id osb_database
  from sp_metricplot
 where mp_metricname = 'OS'
   and mp_metricacronym = 'BUSY'
 order by mp_id;

comment on table vwOsBusy is 'Operating System Metrics [OS Busy] by database';

comment on column vwOsBusy.osb_metric is 'Operating System Metrics [OS Busy] category';
comment on column vwOsBusy.osb_acronym is 'Operating System Metrics [OS Busy] Collection sub-category';
comment on column vwOsBusy.osb_instance is 'Operating System Metrics [OS Busy] Database Instance';
comment on column vwOsBusy.osb_date is 'Operating System Metrics [OS Busy] Collection point in time';
comment on column vwOsBusy.osb_value is 'Operating System Metrics [OS Busy] Collection data metric value';
comment on column vwOsBusy.osb_database is 'Operating System Metrics [OS Busy] associated to the collection';

