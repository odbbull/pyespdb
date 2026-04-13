update sp_category set cat_yaxis_unit = "PGA Size (MB)", cat_yaxis_divisor=1048576, add_interval_fg=0, is_static_fg = 0
   where cat_name = 'MEM' and cat_acronym = 'PGA';
update sp_category set cat_yaxis_unit = "SGA Size (MB)", cat_yaxis_divisor=1048576, add_interval_fg=0
   where cat_name = 'MEM' and cat_acronym = 'SGA';
