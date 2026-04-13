create table sp_DbMaxTotals (
   dmt_dbid		NUMBER(15) NOT NULL,
   dmt_dbname		VARCHAR2(30) NOT NULL,
   dmt_coll_id		NUMBER(15) NOT NULL,
   dmt_storage_total	NUMBER(15),
   dmt_mbps_total	NUMBER(15),
   dmt_cpu_total	NUMBER(15),
   dmt_network_total	NUMBER(15),
   dmt_iops_total	NUMBER(15),
   dmt_ic_total         NUMBER(15),
   dmt_memory_total	NUMBER(15),
   dmt_physio_total	NUMBER(15),
   dmt_directio_total	NUMBER(15),
   dmt_cacheio_total	NUMBER(15),
   PRIMARY KEY (dmt_dbid),
   FOREIGN KEY (dmt_coll_id) REFERENCES sp_collection(coll_id)
);

comment on table sp_DbMaxTotals is 'Establishes the sum of all maximum values for detail categories';

comment on column sp_DbMaxTotals.dmt_dbid is 'The database id associated with the collection';
comment on column sp_DbMaxTotals.dmt_dbname is 'The database name associated with the collection';
comment on column sp_DbMaxTotals.dmt_coll_id is 'The collection id associated with the associated project';
comment on column sp_DbMaxTotals.dmt_storage_total is 'The sum of all maximum DISK category values in gigabytes by database';
comment on column sp_DbMaxTotals.dmt_mbps_total is 'The sum of all maximum MBPS category metrics by database';
comment on column sp_DbMaxTotals.dmt_cpu_total is 'The sum of all maximum session (CPU) category values by database';
comment on column sp_DbMaxTotals.dmt_network_total is 'The sum of all maximum NETWORK (NETW) metrics by database';
comment on column sp_DbMaxTotals.dmt_iops_total is 'The sum of all maximum IOPS metrics by database';
comment on column sp_DbMaxTotals.dmt_ic_total is 'The sum of all maximum interconnect (IC) metrics by database';
comment on column sp_DbMaxTotals.dmt_memory_total is 'The sum of all maximum MEMORY (MEM) values by database';
comment on column sp_DbMaxTotals.dmt_physio_total is 'The sum of all physical IO (PHYR,PHYW) metrics by database';
comment on column sp_DbMaxTotals.dmt_directio_total is 'The sum of all direct IO (PHYRD,PHYRW) metrics by database';
comment on column sp_DbMaxTotals.dmt_cacheio_total is 'The sum of all cache IO (PHYRC,PHYRC) metrics by database';
