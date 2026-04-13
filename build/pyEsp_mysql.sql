CREATE TABLE sp_client (
    cl_id            INTEGER NOT NULL AUTO_INCREMENT,
    cl_name          VARCHAR(30) NOT NULL,
    cl_shortname     VARCHAR(15) NOT NULL,
    cl_creation_date DATETIME NOT NULL,
    is_active_fg     TINYINT,
    cl_account_contact  VARCHAR(30),
    cl_contact_email VARCHAR(30),
    tm_contact       VARCHAR(30),
    tm_contact_email VARCHAR(30),
    cl_modify_date   DATETIME,
    PRIMARY KEY (cl_id)
);

CREATE TABLE sp_collection (
    coll_id              INTEGER NOT NULL AUTO_INCREMENT,
    coll_name            VARCHAR(30) NOT NULL,
    coll_shortname       VARCHAR(15) NOT NULL,
    coll_date            DATETIME NOT NULL,
    is_active_fg         TINYINT NOT NULL,
    coll_dir_location    VARCHAR(255),
    coll_collected_by    VARCHAR(30),
    coll_collector_email VARCHAR(255),
    coll_objective       VARCHAR(255),
    sp_project_pr_id     INTEGER NOT NULL,
    PRIMARY KEY (coll_id),
    FOREIGN KEY (sp_project_pr_id) REFERENCES sp_project(pr_id)
);

CREATE TABLE sp_database (
    db_id                 INTEGER NOT NULL AUTO_INCREMENT,
    db_name               VARCHAR(30) NOT NULL,
    db_shortname          VARCHAR(15) NOT NULL,
    db_filename           VARCHAR(30) NOT NULL,
    db_fileread_date      DATETIME NOT NULL,
    db_collection_host    VARCHAR(30),
    is_cluster_fg         TINYINT,
    is_active_fg          TINYINT,
    sp_collection_coll_id INTEGER NOT NULL,
    PRIMARY KEY (db_id),
    FOREIGN KEY (sp_collection_coll_id) REFERENCES sp_collection(coll_id)
);

CREATE TABLE sp_dbidentity (
    iden_id           INTEGER NOT NULL AUTO_INCREMENT,
    iden_metric       VARCHAR(30),
    iden_acronym      VARCHAR(30),
    iden_instance     INTEGER,
    iden_metricdate   DATETIME,
    iden_metricvalue  VARCHAR(30),
    sp_database_db_id INTEGER NOT NULL,
    PRIMARY KEY (iden_id),
    FOREIGN KEY (sp_database_db_id) REFERENCES sp_database(db_id)
);

CREATE TABLE sp_dbmetric (
    metr_id           INTEGER NOT NULL AUTO_INCREMENT,
    metr_metric       VARCHAR(30),
    metr_acronym      VARCHAR(30),
    metr_instance     INTEGER,
    metr_metricdate   DATETIME,
    metr_metricvalue  TINYINT,
    sp_database_db_id INTEGER NOT NULL,
    PRIMARY KEY (metr_id),
    FOREIGN KEY (sp_database_db_id) REFERENCES sp_database(db_id)
);

CREATE TABLE sp_project (
    pr_id            INTEGER NOT NULL AUTO_INCREMENT,
    pr_name          VARCHAR(30) NOT NULL,
    pr_shortname     VARCHAR(15) NOT NULL,
    pr_creation_date DATETIME NOT NULL,
    is_active_fg     TINYINT,
    pr_modify_date   DATETIME,
    sp_client_cl_id  INTEGER NOT NULL,
    PRIMARY KEY (pr_id),
    FOREIGN KEY (sp_client_cl_id) REFERENCES sp_client(cl_id)
);

CREATE TABLE sp_user (
    us_id           INTEGER NOT NULL AUTO_INCREMENT,
    us_username     VARCHAR(15) NOT NULL,
    us_password     VARCHAR(15) NOT NULL,
    us_first_name   VARCHAR(15),
    us_last_name    VARCHAR(15) NOT NULL,
    is_su_fg        TINYINT,
    is_active_fg    TINYINT NOT NULL,
    us_organization VARCHAR(15),
    PRIMARY KEY (us_id)
);

CREATE TABLE user_client_xref (
    uc_us_id        INTEGER NOT NULL,
    uc_cl_id        INTEGER NOT NULL,
    is_active_fg    TINYINT NOT NULL,
    sp_user_us_id   INTEGER NOT NULL,
    sp_client_cl_id INTEGER NOT NULL
);

