create or replace view vwDbReadIOPS as
select mp_id rio_id,
       mp_metricname rio_metric,
       mp_metricacronym rio_acronym,
       mp_instance rio_instance,
       mp_plotdate rio_date,
       mp_plotvalue rio_value,
       sp_database_db_id rio_database
  from sp_metricplot
 where mp_metricname = 'IOPS'
   and mp_metricacronym = 'RREQS'
 order by mp_id;

comment on table vwDbReadIOPS is 'Storage Read IO per Second (IOPS) by database';

comment on column vwDbReadIOPS.rio_metric is 'Storage Read IO per Second (IOPS) category';
comment on column vwDbReadIOPS.rio_acronym is 'Storage Read IO per Second (IOPS) Collection sub-category';
comment on column vwDbReadIOPS.rio_instance is 'Storage Read IO per Second (IOPS) Database Instance';
comment on column vwDbReadIOPS.rio_date is 'Storage Read IO per Second (IOPS) Collection point in time';
comment on column vwDbReadIOPS.rio_value is 'Storage Read IO per Second (IOPS) Collection data metric value';
comment on column vwDbReadIOPS.rio_database is 'Storage Read IO per Second (IOPS) associated to the collection';

