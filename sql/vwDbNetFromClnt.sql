create or replace view vwDbNetFromClnt as
select mp_id nfc_id,
       mp_metricname nfc_metric,
       mp_metricacronym nfc_acronym,
       mp_instance nfc_instance,
       mp_plotdate nfc_date,
       mp_plotvalue nfc_value,
       sp_database_db_id nfc_database
  from sp_metricplot
 where mp_metricname = 'NETW'
   and mp_metricacronym = 'FROMCLIENT'
 order by mp_id;

comment on table vwDbNetFromClnt is 'Network traffic from client by database';

comment on column vwDbNetFromClnt.nfc_metric is 'Network traffic from client category';
comment on column vwDbNetFromClnt.nfc_acronym is 'Network traffic from client Collection sub-category';
comment on column vwDbNetFromClnt.nfc_instance is 'Network traffic from client Database Instance';
comment on column vwDbNetFromClnt.nfc_date is 'Network traffic from client Collection point in time';
comment on column vwDbNetFromClnt.nfc_value is 'Network traffic from client Collection data metric value';
comment on column vwDbNetFromClnt.nfc_database is 'Network traffic from client associated to the collection';

