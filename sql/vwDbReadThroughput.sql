create or replace view vwDbReadThroughput as
select mp_id dtp_id,
       mp_metricname rtp_metric,
       mp_metricacronym rtp_acronym,
       mp_instance rtp_instance,
       mp_plotdate rtp_date,
       mp_plotvalue rtp_value,
       sp_database_db_id rtp_database
  from sp_metricplot
 where mp_metricname = 'MBPS'
   and mp_metricacronym = 'RBYTES'
 order by mp_id;

comment on table vwDbReadThroughput is 'Read throughput by database';

comment on column vwDbReadThroughput.rtp_metric is 'Read throughput Collection category';
comment on column vwDbReadThroughput.rtp_acronym is 'Read throughput Collection sub-category';
comment on column vwDbReadThroughput.rtp_instance is 'Read throughput Database Instance';
comment on column vwDbReadThroughput.rtp_date is 'Read throughput Collection point in time';
comment on column vwDbReadThroughput.rtp_value is 'Read throughput Collection data metric value';
comment on column vwDbReadThroughput.rtp_database is 'Read throughput Database associated to the collection';

