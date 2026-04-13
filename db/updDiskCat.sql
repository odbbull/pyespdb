update sp_category set cat_yaxis_unit = "Sessions on CPU", cat_yaxis_divisor=1, add_interval_fg=0
   where cat_name = 'CPU' and cat_acronym = 'CPU';
update sp_category set cat_yaxis_unit = "Resource Mgmt (CPU)", cat_yaxis_divisor=1, add_interval_fg=0
   where cat_name = 'CPU' and cat_acronym = 'RMCPUQ';
update sp_category set cat_yaxis_unit = "GB", cat_yaxis_divisor=1048576, add_interval_fg=0
   where cat_name = 'DISK' and cat_acronym = 'LOG';
update sp_category set cat_yaxis_unit = "GB", cat_yaxis_divisor=1048576, add_interval_fg=0
   where cat_name = 'DISK' and cat_acronym = 'PERM';
update sp_category set cat_yaxis_unit = "GB", cat_yaxis_divisor=1048576, add_interval_fg=0
   where cat_name = 'DISK' and cat_acronym = 'TEMP';
update sp_category set cat_yaxis_unit = "GB", cat_yaxis_divisor=1048576, add_interval_fg=0
   where cat_name = 'DISK' and cat_acronym = 'UNDO';
