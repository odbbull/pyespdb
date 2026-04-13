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
   ('EC2 Installation', 
    'ec2',
    curdate(),
    1,
    '/Users/henry.d.tullis/OneDrive - Accenture/1Accenture/2Client/3USA/vistra/Marcus_Hank/eSP',
    'VistraDBA',
    'VistraDBA',
    'EC2 Production and non-Production Environments',
    3);
