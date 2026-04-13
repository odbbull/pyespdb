-- ============================================================
-- populate_sp_host.sql
-- Populates sp_host from sp_dbidentity HOST_NAME / INSTANCE_NAME
--
-- hs_name      = hostname  (HOST_NAME metricvalue)
-- hs_location  = Oracle instance name string (e.g. 'amlprd01')
-- hs_instance  = numeric instance number extracted from instance name:
--                  standard format  amlprd01   → RIGHT(value,2)::numeric  → 1
--                  underscore fmt   crnprd00_2 → SPLIT_PART(value,'_',2)::numeric → 2
-- is_active_fg = true
-- sp_exaframe_fr_id = NULL (populate separately if needed)
-- ============================================================

BEGIN;

INSERT INTO sp_host (hs_name, hs_location, hs_instance, is_active_fg, sp_exaframe_fr_id)
SELECT
    LEFT(h.iden_metricvalue, 30)  AS hs_name,
    LEFT(i.iden_metricvalue, 30)  AS hs_location,
    CASE
        WHEN i.iden_metricvalue LIKE '%\_%' ESCAPE '\'
            THEN SPLIT_PART(i.iden_metricvalue, '_', 2)::numeric
        ELSE RIGHT(i.iden_metricvalue, 2)::numeric
    END                           AS hs_instance,
    true                          AS is_active_fg,
    NULL                          AS sp_exaframe_fr_id
FROM sp_dbidentity h
JOIN sp_dbidentity i
    ON h.sp_database_db_id = i.sp_database_db_id
    AND h.iden_instance    = i.iden_instance
    AND i.iden_acronym     = 'INSTANCE_NAME'
WHERE h.iden_acronym = 'HOST_NAME'
ORDER BY h.sp_database_db_id, h.iden_instance;

-- Verify row count and instance number distribution
SELECT COUNT(*) AS rows_inserted FROM sp_host;

SELECT hs_instance, COUNT(*) AS cnt
FROM sp_host
GROUP BY hs_instance
ORDER BY hs_instance;

COMMIT;
