create or replace view vwDbRedoThroughput as
select mp_id dtp_id,
       mp_metricname dtp_metric,
       mp_metricacronym dtp_acronym,
       mp_instance dtp_instance,
       mp_plotdate dtp_date,
       mp_plotvalue dtp_value,
       sp_database_db_id dtp_database
  from sp_metricplot
 where mp_metricname = 'MBPS'
   and mp_metricacronym = 'WREDOBYTES'
 order by mp_id;

comment on table vwDbRedoThroughput is 'Redo throughput by database';

comment on column vwDbRedoThroughput.dtp_metric is 'Redo throughput Collection category';
comment on column vwDbRedoThroughput.dtp_acronym is 'Redo throughput Collection sub-category';
comment on column vwDbRedoThroughput.dtp_instance is 'Redo throughput Database Instance';
comment on column vwDbRedoThroughput.dtp_date is 'Redo throughput Collection point in time';
comment on column vwDbRedoThroughput.dtp_value is 'Redo throughput Collection data metric value';
comment on column vwDbRedoThroughput.dtp_database is 'Redo throughput Database associated to the collection';

