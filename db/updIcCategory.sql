update sp_category set cat_yaxis_unit = "IC Blocks Received", cat_yaxis_divisor=1, add_interval_fg=0
   where cat_name = 'IC' and cat_acronym = 'GCCBLR';
update sp_category set cat_yaxis_unit = "IC Blocks Sent", cat_yaxis_divisor=1, add_interval_fg=0
   where cat_name = 'IC' and cat_acronym = 'GCCBLS';
update sp_category set cat_yaxis_unit = "IC MBytes Received", cat_yaxis_divisor=1048576, add_interval_fg=0
   where cat_name = 'IC' and cat_acronym = 'GCCRBR';
update sp_category set cat_yaxis_unit = "IC MBytes Sent", cat_yaxis_divisor=1048576, add_interval_fg=0
   where cat_name = 'IC' and cat_acronym = 'GCCRBS';
update sp_category set cat_yaxis_unit = "IC Cache Messages Received", cat_yaxis_divisor=1, add_interval_fg=0
   where cat_name = 'IC' and cat_acronym = 'GCSMR';
update sp_category set cat_yaxis_unit = "IC Cache Messages Sent", cat_yaxis_divisor=1, add_interval_fg=0
   where cat_name = 'IC' and cat_acronym = 'GCSMS';
update sp_category set cat_yaxis_unit = "IC Enqueue Messages Received", cat_yaxis_divisor=1, add_interval_fg=0
   where cat_name = 'IC' and cat_acronym = 'GESMR';
update sp_category set cat_yaxis_unit = "IC Enqueue Messages Sent", cat_yaxis_divisor=1, add_interval_fg=0
   where cat_name = 'IC' and cat_acronym = 'GESMS';
