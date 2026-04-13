update sp_category set cat_yaxis_unit = "OS Percent Busy", cat_yaxis_divisor=100, add_interval_fg=0
   where cat_name = 'OS' and cat_acronym = 'OSBUSY';
update sp_category set cat_yaxis_unit = "OS Number of Cores", cat_yaxis_divisor=100, add_interval_fg=0
   where cat_name = 'OS' and cat_acronym = 'OSCORES';
update sp_category set cat_yaxis_unit = "OS Number of CPU", cat_yaxis_divisor=100, add_interval_fg=0
   where cat_name = 'OS' and cat_acronym = 'OSCPUS';
update sp_category set cat_yaxis_unit = "OS Percent Idle", cat_yaxis_divisor=100, add_interval_fg=0
   where cat_name = 'OS' and cat_acronym = 'OSIDLE';
update sp_category set cat_yaxis_unit = "OS Percent IO Wait", cat_yaxis_divisor=100, add_interval_fg=0
   where cat_name = 'OS' and cat_acronym = 'OSIOWAIT';
update sp_category set cat_yaxis_unit = "OS Load Average", cat_yaxis_divisor=100, add_interval_fg=0
   where cat_name = 'OS' and cat_acronym = 'OSLOAD';
update sp_category set cat_yaxis_unit = "OS Total Memory (MB)", cat_yaxis_divisor=1048576, add_interval_fg=0, is_static_fg = 1
   where cat_name = 'OS' and cat_acronym = 'OSMEMBYTES';
update sp_category set cat_yaxis_unit = "OS Sys Nice Wait", cat_yaxis_divisor=100, add_interval_fg=0
   where cat_name = 'OS' and cat_acronym = 'OSNICEWAIT';
update sp_category set cat_yaxis_unit = "OS Percent System", cat_yaxis_divisor=100, add_interval_fg=0
   where cat_name = 'OS' and cat_acronym = 'OSSYS';
update sp_category set cat_yaxis_unit = "OS Percent User", cat_yaxis_divisor=100, add_interval_fg=0
   where cat_name = 'OS' and cat_acronym = 'OSUSER';
update sp_category set cat_yaxis_unit = "OS Percent ResMgmt", cat_yaxis_divisor=100, add_interval_fg=0
   where cat_name = 'OS' and cat_acronym = 'RMCPUWAIT';
