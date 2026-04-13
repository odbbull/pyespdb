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
   ('SQLServer Prod', 
    'sql prod',
    curdate(),
    1,
    '/Users/htullis/1Deloitte/Tools/AcmeAnvil/util/VanguardSQLServers.xlsx',
    'Santosh Hulage',
    'santosh_hulage@vanguard.com',
    'Perform on-premises sizing and provisioning',
    1);
