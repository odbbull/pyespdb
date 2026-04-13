CREATE TABLE sp_client (
    cl_id            NUMBER(15) NOT NULL,
    cl_name          VARCHAR2(30) NOT NULL,
    cl_shortname     VARCHAR2(15) NOT NULL,
    cl_creation_date DATE NOT NULL,
    is_active_fg     BOOLEAN,
    cl_account_contact  VARCHAR2(30),
    cl_contact_email VARCHAR2(30),
    tm_contact       VARCHAR2(30),
    tm_contact_email VARCHAR2(30),
    cl_modify_date   DATE,
    PRIMARY KEY (cl_id)
);

CREATE TABLE sp_collection (
    coll_id              NUMBER(15) NOT NULL,
    coll_name            VARCHAR2(30) NOT NULL,
    coll_shortname       VARCHAR2(15) NOT NULL,
    coll_date            DATE NOT NULL,
    is_active_fg         BOOLEAN NOT NULL,
    coll_dir_location    VARCHAR2(255),
    coll_collected_by    VARCHAR2(30),
    coll_collector_email VARCHAR2(255),
    coll_objective       VARCHAR2(255),
    sp_project_pr_id     NUMBER(15) NOT NULL,
    PRIMARY KEY (coll_id),
    FOREIGN KEY (sp_project_pr_id) REFERENCES sp_project(pr_id)
);

CREATE TABLE sp_database (
    db_id                 NUMBER(15) NOT NULL,
    db_name               VARCHAR2(30) NOT NULL,
    db_shortname          VARCHAR2(15) NOT NULL,
    db_filename           VARCHAR2(30) NOT NULL,
    db_fileread_date      DATE NOT NULL,
    db_collection_host    VARCHAR2(30),
    is_cluster_fg         BOOLEAN,
    is_active_fg          BOOLEAN,
    sp_collection_coll_id NUMBER(15) NOT NULL,
    PRIMARY KEY (db_id),
    FOREIGN KEY (sp_collection_coll_id) REFERENCES sp_collection(coll_id)
);

CREATE TABLE sp_dbidentity (
    iden_id           NUMBER(15) NOT NULL,
    iden_metric       VARCHAR2(30),
    iden_acronym      VARCHAR2(30),
    iden_instance     INTEGER,
    iden_metricdate   DATE,
    iden_metricvalue  VARCHAR2(30),
    sp_database_db_id NUMBER(15) NOT NULL,
    PRIMARY KEY (iden_id),
    FOREIGN KEY (sp_database_db_id) REFERENCES sp_database(db_id)
);

CREATE TABLE sp_dbmetric (
    metr_id           NUMBER(15) NOT NULL,
    metr_metric       VARCHAR2(30),
    metr_acronym      VARCHAR2(30),
    metr_instance     INTEGER,
    metr_metricdate   DATE,
    metr_metricvalue  BOOLEAN,
    sp_database_db_id NUMBER(15) NOT NULL,
    PRIMARY KEY (metr_id),
    FOREIGN KEY (sp_database_db_id) REFERENCES sp_database(db_id)
);

CREATE TABLE sp_project (
    pr_id            NUMBER(15) NOT NULL,
    pr_name          VARCHAR2(30) NOT NULL,
    pr_shortname     VARCHAR2(15) NOT NULL,
    pr_creation_date DATE NOT NULL,
    is_active_fg     BOOLEAN,
    pr_modify_date   DATE,
    sp_client_cl_id  NUMBER(15) NOT NULL,
    PRIMARY KEY (pr_id),
    FOREIGN KEY (sp_client_cl_id) REFERENCES sp_client(cl_id)
);

CREATE TABLE sp_user (
    us_id           NUMBER(15) NOT NULL,
    us_username     VARCHAR2(15) NOT NULL,
    us_password     VARCHAR2(15) NOT NULL,
    us_first_name   VARCHAR2(15),
    us_last_name    VARCHAR2(15) NOT NULL,
    is_su_fg        BOOLEAN,
    is_active_fg    BOOLEAN NOT NULL,
    us_organization VARCHAR2(15),
    PRIMARY KEY (us_id)
);

CREATE TABLE user_client_xref (
    uc_us_id        NUMBER(15) NOT NULL,
    uc_cl_id        NUMBER(15) NOT NULL,
    is_active_fg    BOOLEAN NOT NULL,
    sp_user_us_id   NUMBER(15) NOT NULL,
    sp_client_cl_id NUMBER(15) NOT NULL
);

CREATE TABLE vg_DbRetirement (
   vg_id	    NUMBER(15) NOT NULL,
   vg_dbName        VARCHAR2(30),
   vg_subdivision   VARCHAR2(75),
   vg_application   VARCHAR2(255),
   vg_disposition   VARCHAR2(75),
   vg_dispQuarter   VARCHAR2(25),
   vg_dispYear      INTEGER,
   vg_comment       VARCHAR2(255),
   PRIMARY KEY (vg_id)
);

CREATE TABLE sp_dbmetric_summ (
  ms_id             NUMBER(15) NOT NULL,
  ms_metric         VARCHAR2(30) NOT NULL,
  ms_acronym        VARCHAR2(30) NOT NULL,
  ms_instance       NUMBER DEFAULT NULL,
  ms_avgvalue       VARCHAR2(30) DEFAULT NULL,
  ms_maxvalue       VARCHAR2(30) DEFAULT NULL,
  sp_database_db_id NUMBER(15) DEFAULT NULL,
  PRIMARY KEY (ms_id),
  FOREIGN KEY (sp_database_db_id) REFERENCES sp_database (db_id)
);

CREATE TABLE sp_ExaFrame (
  fr_id            NUMBER(15) NOT NULL,
  fr_name          VARCHAR2(30) NOT NULL,
  fr_location      VARCHAR2(30) NOT NULL,
  fr_model         VARCHAR2(30) DEFAULT NULL,
  is_active_fg     BOOLEAN DEFAULT NULL,
  PRIMARY KEY (fr_id)
);

CREATE TABLE sp_host (
  hs_id             NUMBER(15) NOT NULL,
  hs_name           VARCHAR2(30) NOT NULL,
  hs_location       VARCHAR2(30) NOT NULL,
  hs_instance       NUMBER DEFAULT NULL,
  is_active_fg      BOOLEAN DEFAULT NULL,
  sp_exaframe_fr_id NUMBER DEFAULT NULL,
  PRIMARY KEY (hs_id),
  FOREIGN KEY (sp_exaframe_fr_id) REFERENCES sp_exaframe (fr_id)
);

CREATE TABLE sp_MetricPlot (
  mp_id             NUMBER NOT NULL,
  mp_metricName     VARCHAR2(30) NOT NULL,
  mp_metricAcronym  VARCHAR2(30) NOT NULL,
  mp_instance       NUMBER DEFAULT NULL,
  mp_plotdate       DATE DEFAULT NULL,
  mp_plotvalue      VARCHAR2(75) DEFAULT NULL,
  sp_database_db_id NUMBER(15) NOT NULL,
  PRIMARY KEY (mp_id),
  FOREIGN KEY (sp_database_db_id) REFERENCES sp_database (db_id)
); 

CREATE TABLE sp_category (
  cat_id            NUMBER(15) NOT NULL,
  cat_name          VARCHAR2(30) NOT NULL,
  cat_acronym       VARCHAR2(15) NOT NULL,
  is_static_fg      BOOLEAN DEFAULT NULL,
  is_active_fg      BOOLEAN DEFAULT NULL,
  cat_yaxis_unit    VARCHAR2(75) DEFAULT NULL,
  cat_yaxis_divisor NUMBER DEFAULT NULL,
  add_interval_fg   BOOLEAN DEFAULT NULL,
  PRIMARY KEY (cat_id)
);
