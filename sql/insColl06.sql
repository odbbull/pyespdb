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
   ('Gulfstream Prod', 
    'GS Prod',
    curdate(),
    1,
    '/Users/htullis/OneDrive/OneDrive - Deloitte (O365D)/Gulfstream Collection Files/escp_output_prod',
    'Mark Saltzman',
    'msaltzman@deloitte.com',
    'application review for performance and provisioning',
    2);

