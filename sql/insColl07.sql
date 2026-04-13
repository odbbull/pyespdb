insert into sp_collection
   (coll_name, 
    coll_shortname, 
    coll_date, 
    is_active_fg, 
    coll_dir_location, 
    coll_collected_by, 
    coll_collector_email, 
    coll_objective, 
    sp_project_pr_id)
 values
   ('Point32Health Exadata', 
    'P32 Legacy',
    curdate(),
    1,
    '/Users/htullis/OneDrive/OneDrive - Deloitte (O365D)/Point32Health/escp_output_legacy',
    'Mikhail Gurevich',
    'migurevich@deloitte.com',
    'legacy exadata performance review for analysis',
    3);

