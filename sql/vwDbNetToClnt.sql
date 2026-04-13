create or replace view vwDbNettoClnt as
select mp_id ntc_id,
       mp_metricname ntc_metric,
       mp_metricacronym ntc_acronym,
       mp_instance ntc_instance,
       mp_plotdate ntc_date,
       mp_plotvalue ntc_value,
       sp_database_db_id ntc_database
  from sp_metricplot
 where mp_metricname = 'NETW'
   and mp_metricacronym = 'TOCLIENT'
 order by mp_id;

comment on table vwDbNettoClnt is 'Network traffic to client by database';

comment on column vwDbNettoClnt.ntc_metric is 'Network traffic to client category';
comment on column vwDbNettoClnt.ntc_acronym is 'Network traffic to client Collection sub-category';
comment on column vwDbNettoClnt.ntc_instance is 'Network traffic to client Database Instance';
comment on column vwDbNettoClnt.ntc_date is 'Network traffic to client Collection point in time';
comment on column vwDbNettoClnt.ntc_value is 'Network traffic to client Collection data metric value';
comment on column vwDbNettoClnt.ntc_database is 'Network traffic to client associated to the collection';

