insert into sp_project
   (pr_name, 
    pr_shortname, 
    pr_creation_date, 
    is_active_fg, 
    sp_client_cl_id)
 values
   ('Vistra EC2', 
    'vistra',
    curdate(),
    1,
    2);
