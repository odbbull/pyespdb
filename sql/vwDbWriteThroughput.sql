create or replace view vwDbWriteThroughput as
select mp_id dtp_id,
       mp_metricname wtp_metric,
       mp_metricacronym wtp_acronym,
       mp_instance wtp_instance,
       mp_plotdate wtp_date,
       mp_plotvalue wtp_value,
       sp_database_db_id wtp_database
  from sp_metricplot
 where mp_metricname = 'MBPS'
   and mp_metricacronym = 'WBYTES'
 order by mp_id;

comment on table vwDbWriteThroughput is 'Write throughput by database';

comment on column vwDbWriteThroughput.wtp_metric is 'Write throughput Collection category';
comment on column vwDbWriteThroughput.wtp_acronym is 'Write throughput Collection sub-category';
comment on column vwDbWriteThroughput.wtp_instance is 'Write throughput Database Instance';
comment on column vwDbWriteThroughput.wtp_date is 'Write throughput Collection point in time';
comment on column vwDbWriteThroughput.wtp_value is 'Write throughput Collection data metric value';
comment on column vwDbWriteThroughput.wtp_database is 'Write throughput Database associated to the collection';

