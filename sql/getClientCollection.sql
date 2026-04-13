select c.cl_id, c.cl_name, a.coll_dir_location
  from sp_collection a,
       sp_project p,
       sp_client c
 where a.coll_id = 1
   and a.sp_project_pr_id = p.pr_id
   and p.sp_client_cl_id = c.cl_id;
