create or replace view vwOsUser as
select mp_id osu_id,
       mp_metricname osu_metric,
       mp_metricacronym osu_acronym,
       mp_instance osu_instance,
       mp_plotdate osu_date,
       mp_plotvalue osu_value,
       sp_database_db_id osu_database
  from sp_metricplot
 where mp_metricname = 'OS'
   and mp_metricacronym = 'OSUSER'
 order by mp_id;

comment on table vwOsUser is 'Operating User Metrics [OS User] by database';

comment on column vwOsUser.osu_metric is 'Operating User Metrics [OS User] category';
comment on column vwOsUser.osu_acronym is 'Operating User Metrics [OS User] Collection sub-category';
comment on column vwOsUser.osu_instance is 'Operating User Metrics [OS User] Database Instance';
comment on column vwOsUser.osu_date is 'Operating User Metrics [OS User] Collection point in time';
comment on column vwOsUser.osu_value is 'Operating User Metrics [OS User] Collection data metric value';
comment on column vwOsUser.osu_database is 'Operating User Metrics [OS User] associated to the collection';

