import os
import mysql.connector
from mysql.connector import errorcode

vCollId = "5"
pyespConn = ''
vCursor = ''
vQuery = ''
vClientInfo = ''

try:
   pyespConn = mysql.connector.connect(user='pyesp', password='welcome1',
                                      host='127.0.0.1', database='pyespdb')
except mysql.connector.Error as err:
   if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print(f"Something is wrong with username and password")
   elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print(f"Database does not exist")
   else:
      print(err)

vCursor = pyespConn.cursor()

vQuery = "select c.cl_id, c.cl_name, a.coll_dir_location \
            from sp_collection a,                        \
                 sp_project p,                           \
                 sp_client c                             \
           where a.coll_id = %s                          \
             and a.sp_project_pr_id = p.pr_id            \
             and p.sp_client_cl_id = c.cl_id" 

vCursor.execute(vQuery, (vCollId,))

vClientInfo = vCursor.fetchone()

# for vInfo in vClientInfo:
print (vClientInfo[2])

vDirLoc = vClientInfo[2]
vDirSet = os.listdir(vDirLoc)
# vTmpDir = os.mkdir("/tmp/espHome")

print (vDirSet)
for vDir in vDirSet:
  vHostDir = vDirLoc +"/"+vDir
  print (vHostDir)
  vHostFiles = os.listdir(vHostDir)

  for vFile in vHostFiles:
     print(vFile)

     vParts = vFile.split("_")
     print(vParts[2], vParts[3])

vCursor.close()
pyespConn.close()
