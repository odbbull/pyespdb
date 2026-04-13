update sp_category set cat_yaxis_unit = "Read Requests per Sec", cat_yaxis_divisor=1, add_interval_fg=1
   where cat_name = 'IOPS' and cat_acronym = 'RREQS';
update sp_category set cat_yaxis_unit = "Write Requests per Sec", cat_yaxis_divisor=1, add_interval_fg=1
   where cat_name = 'IOPS' and cat_acronym = 'WREQS';
update sp_category set cat_yaxis_unit = "Redo Requests per Sec", cat_yaxis_divisor=1, add_interval_fg=1
    where cat_name = 'IOPS' and cat_acronym = 'WREDO';
update sp_category set cat_yaxis_unit = "Data Read (MBPS)", cat_yaxis_divisor=1048576, add_interval_fg=1
    where cat_name = 'MBPS' and cat_acronym = 'RBYTES';
update sp_category set cat_yaxis_unit = "Data Writes (MBPS)", cat_yaxis_divisor=1048576, add_interval_fg=1
    where cat_name = 'MBPS' and cat_acronym = 'WBYTES';
update sp_category set cat_yaxis_unit = "Redo Data Writes (MBPS)", cat_yaxis_divisor=1048576, add_interval_fg=1
    where cat_name = 'MBPS' and cat_acronym = 'WREDOBYTES';
update sp_category set cat_yaxis_unit = "Bytes from Client", cat_yaxis_divisor=1, add_interval_fg=0
    where cat_name = 'NETW' and cat_acronym = 'FROMCLIENT';
update sp_category set cat_yaxis_unit = "Bytes from DBLink", cat_yaxis_divisor=1, add_interval_fg=0
    where cat_name = 'NETW' and cat_acronym = 'FROMDBLINK';
update sp_category set cat_yaxis_unit = "Bytes to Client", cat_yaxis_divisor=1, add_interval_fg=0
    where cat_name = 'NETW' and cat_acronym = 'TOCLIENT';
update sp_category set cat_yaxis_unit = "Bytes to DBLink", cat_yaxis_divisor=1, add_interval_fg=0
    where cat_name = 'NETW' and cat_acronym = 'TODBLINK';
update sp_category set cat_yaxis_unit = "Physical Reads", cat_yaxis_divisor=1, add_interval_fg=0
    where cat_name = 'PHYR' and cat_acronym = 'PHYR';
update sp_category set cat_yaxis_unit = "Physical Reads from Cache", cat_yaxis_divisor=1, add_interval_fg=0
    where cat_name = 'PHYR' and cat_acronym = 'PHYRC';
update sp_category set cat_yaxis_unit = "Physical Reads Direct", cat_yaxis_divisor=1, add_interval_fg=0
    where cat_name = 'PHYR' and cat_acronym = 'PHYRD';
update sp_category set cat_yaxis_unit = "Physical Writes", cat_yaxis_divisor=1, add_interval_fg=0
    where cat_name = 'PHYW' and cat_acronym = 'PHYW';
update sp_category set cat_yaxis_unit = "Physical Writes to Cache", cat_yaxis_divisor=1, add_interval_fg=0
    where cat_name = 'PHYW' and cat_acronym = 'PHYWC';
update sp_category set cat_yaxis_unit = "Physical Writes Direct", cat_yaxis_divisor=1, add_interval_fg=0
    where cat_name = 'PHYW' and cat_acronym = 'PHYWD';
