-- PostgreSQL Schema Conversion from Oracle pyEsp_oracle.sql
-- Key changes:
-- 1. NUMBER(15) -> BIGINT with GENERATED ALWAYS AS IDENTITY for auto-increment PKs
-- 2. VARCHAR2 -> VARCHAR
-- 3. BOOLEAN remains BOOLEAN (native in PostgreSQL)
-- 4. DATE -> TIMESTAMP (PostgreSQL DATE is date-only, TIMESTAMP includes time)
-- 5. Using GENERATED ALWAYS AS IDENTITY (PostgreSQL 10+) instead of SERIAL
-- 6. Reordered table creation to respect foreign key dependencies

-- Create tables in dependency order

CREATE TABLE sp_client (
    cl_id            BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    cl_name          VARCHAR(30) NOT NULL,
    cl_shortname     VARCHAR(15) NOT NULL,
    cl_creation_date TIMESTAMP NOT NULL,
    is_active_fg     BOOLEAN,
    cl_account_contact  VARCHAR(30),
    cl_contact_email VARCHAR(30),
    tm_contact       VARCHAR(30),
    tm_contact_email VARCHAR(30),
    cl_modify_date   TIMESTAMP,
    PRIMARY KEY (cl_id)
);

CREATE TABLE sp_user (
    us_id           BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    us_username     VARCHAR(15) NOT NULL,
    us_password     VARCHAR(15) NOT NULL,
    us_first_name   VARCHAR(15),
    us_last_name    VARCHAR(15) NOT NULL,
    is_su_fg        BOOLEAN,
    is_active_fg    BOOLEAN NOT NULL,
    us_organization VARCHAR(15),
    PRIMARY KEY (us_id)
);

CREATE TABLE sp_project (
    pr_id            BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    pr_name          VARCHAR(30) NOT NULL,
    pr_shortname     VARCHAR(15) NOT NULL,
    pr_creation_date TIMESTAMP NOT NULL,
    is_active_fg     BOOLEAN,
    pr_modify_date   TIMESTAMP,
    sp_client_cl_id  BIGINT NOT NULL,
    PRIMARY KEY (pr_id),
    FOREIGN KEY (sp_client_cl_id) REFERENCES sp_client(cl_id)
);

CREATE TABLE sp_collection (
    coll_id              BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    coll_name            VARCHAR(30) NOT NULL,
    coll_shortname       VARCHAR(15) NOT NULL,
    coll_date            TIMESTAMP NOT NULL,
    is_active_fg         BOOLEAN NOT NULL,
    coll_dir_location    VARCHAR(255),
    coll_collected_by    VARCHAR(30),
    coll_collector_email VARCHAR(255),
    coll_objective       VARCHAR(255),
    sp_project_pr_id     BIGINT NOT NULL,
    PRIMARY KEY (coll_id),
    FOREIGN KEY (sp_project_pr_id) REFERENCES sp_project(pr_id)
);

CREATE TABLE sp_exaframe (
    fr_id            BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    fr_name          VARCHAR(30) NOT NULL,
    fr_location      VARCHAR(30) NOT NULL,
    fr_model         VARCHAR(30) DEFAULT NULL,
    is_active_fg     BOOLEAN DEFAULT NULL,
    PRIMARY KEY (fr_id)
);

CREATE TABLE sp_host (
    hs_id             BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    hs_name           VARCHAR(30) NOT NULL,
    hs_location       VARCHAR(30) NOT NULL,
    hs_instance       NUMERIC DEFAULT NULL,
    is_active_fg      BOOLEAN DEFAULT NULL,
    sp_exaframe_fr_id BIGINT DEFAULT NULL,
    PRIMARY KEY (hs_id),
    FOREIGN KEY (sp_exaframe_fr_id) REFERENCES sp_exaframe(fr_id)
);

CREATE TABLE sp_database (
    db_id                 BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    db_name               VARCHAR(30) NOT NULL,
    db_shortname          VARCHAR(15) NOT NULL,
    db_filename           VARCHAR(30) NOT NULL,
    db_fileread_date      TIMESTAMP NOT NULL,
    db_collection_host    VARCHAR(30),
    db_host_cpu           VARCHAR(60),
    db_host_model         VARCHAR(60),
    is_cluster_fg         BOOLEAN,
    is_active_fg          BOOLEAN,
    db_metrics_date       TIMESTAMP DEFAULT NULL,
    sp_host_hs_id         BIGINT DEFAULT NULL,
    sp_collection_coll_id BIGINT NOT NULL,
    PRIMARY KEY (db_id),
    FOREIGN KEY (sp_collection_coll_id) REFERENCES sp_collection(coll_id)
);

CREATE TABLE sp_dbidentity (
    iden_id           BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    iden_metric       VARCHAR(30),
    iden_acronym      VARCHAR(30),
    iden_instance     INTEGER,
    iden_metricdate   TIMESTAMP,
    iden_metricvalue  VARCHAR(30),
    sp_database_db_id BIGINT NOT NULL,
    PRIMARY KEY (iden_id),
    FOREIGN KEY (sp_database_db_id) REFERENCES sp_database(db_id)
);

CREATE TABLE sp_dbmetric (
    metr_id           BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    metr_metric       VARCHAR(30),
    metr_acronym      VARCHAR(30),
    metr_instance     INTEGER,
    metr_metricdate   TIMESTAMP,
    metr_metricvalue  VARCHAR(75),
    sp_database_db_id BIGINT NOT NULL,
    PRIMARY KEY (metr_id),
    FOREIGN KEY (sp_database_db_id) REFERENCES sp_database(db_id)
);

CREATE TABLE sp_dbmetric_summ (
    ms_id             BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    ms_metric         VARCHAR(30) NOT NULL,
    ms_acronym        VARCHAR(30) NOT NULL,
    ms_instance       NUMERIC DEFAULT NULL,
    ms_avgvalue       VARCHAR(30) DEFAULT NULL,
    ms_maxvalue       VARCHAR(30) DEFAULT NULL,
    sp_database_db_id BIGINT DEFAULT NULL,
    PRIMARY KEY (ms_id),
    FOREIGN KEY (sp_database_db_id) REFERENCES sp_database(db_id)
);

CREATE TABLE sp_metricplot (
    mp_id             BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    mp_metricname     VARCHAR(30) NOT NULL,
    mp_metricacronym  VARCHAR(30) NOT NULL,
    mp_instance       NUMERIC DEFAULT NULL,
    mp_plotdate       TIMESTAMP DEFAULT NULL,
    mp_plotvalue      VARCHAR(75) DEFAULT NULL,
    sp_database_db_id BIGINT NOT NULL,
    PRIMARY KEY (mp_id),
    FOREIGN KEY (sp_database_db_id) REFERENCES sp_database(db_id)
);

CREATE TABLE sp_category (
    cat_id            BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    cat_name          VARCHAR(30) NOT NULL,
    cat_acronym       VARCHAR(15) NOT NULL,
    is_static_fg      BOOLEAN DEFAULT NULL,
    is_active_fg      BOOLEAN DEFAULT NULL,
    cat_yaxis_unit    VARCHAR(75) DEFAULT NULL,
    cat_yaxis_divisor NUMERIC DEFAULT NULL,
    add_interval_fg   BOOLEAN DEFAULT NULL,
    PRIMARY KEY (cat_id)
);

CREATE TABLE user_client_xref (
    uc_us_id        BIGINT NOT NULL,
    uc_cl_id        BIGINT NOT NULL,
    is_active_fg    BOOLEAN NOT NULL,
    sp_user_us_id   BIGINT NOT NULL,
    sp_client_cl_id BIGINT NOT NULL,
    FOREIGN KEY (sp_user_us_id) REFERENCES sp_user(us_id),
    FOREIGN KEY (sp_client_cl_id) REFERENCES sp_client(cl_id)
);

-- Optional: Create indexes for foreign keys (PostgreSQL doesn't auto-index FKs like Oracle)
CREATE INDEX idx_sp_project_client ON sp_project(sp_client_cl_id);
CREATE INDEX idx_sp_collection_project ON sp_collection(sp_project_pr_id);
CREATE INDEX idx_sp_database_collection ON sp_database(sp_collection_coll_id);
CREATE INDEX idx_sp_dbidentity_database ON sp_dbidentity(sp_database_db_id);
CREATE INDEX idx_sp_dbmetric_database ON sp_dbmetric(sp_database_db_id);
CREATE INDEX idx_sp_dbmetric_summ_database ON sp_dbmetric_summ(sp_database_db_id);
CREATE INDEX idx_sp_metricplot_database ON sp_metricplot(sp_database_db_id);
CREATE INDEX idx_sp_host_exaframe ON sp_host(sp_exaframe_fr_id);
CREATE INDEX idx_user_client_xref_user ON user_client_xref(sp_user_us_id);
CREATE INDEX idx_user_client_xref_client ON user_client_xref(sp_client_cl_id);

-- Optional: Add comments for documentation
COMMENT ON TABLE sp_client IS 'Client information for ESCP monitoring system';
COMMENT ON TABLE sp_database IS 'Database instances being monitored';
COMMENT ON TABLE sp_dbmetric IS 'Database performance metrics';
COMMENT ON TABLE sp_exaframe IS 'Exadata frame information';

-- ── Migrations ────────────────────────────────────────────────────────────────
-- Run these ALTER statements against an existing database that was created
-- before the corresponding column was added to the schema above.

-- 2026-03-03: track when metric plots were last generated for each database
ALTER TABLE sp_database ADD COLUMN IF NOT EXISTS db_metrics_date TIMESTAMP DEFAULT NULL;

-- 2026-04-13: add hidden_name to sp_client
ALTER TABLE sp_client ADD COLUMN IF NOT EXISTS hidden_name VARCHAR(50) DEFAULT NULL;
