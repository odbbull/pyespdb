select distinct sp_collection_coll_id,
       coll_name,
       cl_name,
       pr_name,
       count(db_id)
  from sp_database, sp_collection, sp_project, sp_client
 where sp_collection_coll_id = coll_id
   and sp_project_pr_id = pr_id
   and sp_client_cl_id = cl_id
 group by cl_name, pr_name, sp_collection_coll_id, coll_name
 order by 1;
