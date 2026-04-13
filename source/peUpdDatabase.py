from optparse       import OptionParser
from os.path        import basename
from sys            import argv
from sys            import exit
import datetime
from datetime import datetime
import os
import csv
import mysql.connector
from mysql.connector import errorcode

def getDBConnection():

   try:
       acmeConn = mysql.connector.connect(user='acme', password='welcome1',
                                         host='127.0.0.1', database='AcmeAnvil')
   except mysql.connector.Error as err:
       if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
          print(f"Something is wrong with username and password")
       elif err.errno == errorcode.ER_BAD_DB_ERROR:
          print(f"Database does not exist")
       else:
          print(err)
   else:
      return (acmeConn)
  
def getClientCollection(pConn, pCollId, pCollDir, pClientId, pClientName):
   
   vCursor = pConn.cursor()
   
   vQuery =  "select c.cl_id, c.cl_name, a.coll_dir_location     \
                from sp_collection a,                            \
                     sp_project p,                               \
                     sp_client c                                 \
               where a.coll_id = %s                              \
                 and a.sp_project_pr_id = p.pr_id                \
                 and p.sp_client_cl_id = c.cl_id;" 

   vCursor.execute(vQuery, (pCollId,))

   vResult = vCursor.fetchone()
   pCollDir = vResult[2]
   pClientId = vResult[0]
   pClientName = vResult[1]

   vCursor.close()

   return pCollDir, pClientId, pClientName

def getHostFile(pHostPath):
   pathSplit = pHostPath.split('/')
   hostFile = pathSplit[8]

   return hostFile

def splitHostFile(pHostFile):
   vFilePart = pHostFile.split("_")
   vHostName = vFilePart[2]
   vDBName = vFilePart[3]
   vDateRead = vFilePart[4]
   vTimeRead = vFilePart[5][0:4]
   
   dateString = vDateRead + vTimeRead
   combDate = datetime.strptime(dateString, '%Y%m%d%H%M')

   return vDBName, combDate, vHostName

def updSpDatabase(pConn, pCollectionId):
   
   vGetCursor = pConn.cursor()
   vUpdCursor = pConn.cursor()
   
   vGetDbQuery = "select db_id, db_filename from sp_database where sp_collection_coll_id = %s"
   
   vUpdQuery = "update sp_database set db_name = %s, db_shortname = %s, db_fileread_date = %s, db_collection_host = %s   \
                 where db_id = %s"

   vGetCursor = pConn.cursor()
   vUpdCursor = pConn.cursor()
                  
   vGetCursor.execute(vGetDbQuery, (pCollectionId,))
   vGetResult = vGetCursor.fetchall()
   
   for result in vGetResult:
      vDatabaseId = result[0]
      vHostPath = result[1]

      vHostFile = getHostFile(vHostPath)
      vDBName, combDate, vHostName = splitHostFile(vHostFile)

      vUpdCursor.execute(vUpdQuery, (vDBName, vDBName, combDate, vHostName, vDatabaseId,))
   
   pConn.commit()
   vUpdCursor.close()

# ----------------------
# ---- Main Program
# ----------------------

if (__name__ == '__main__'):
    cmd         = basename(argv[0])
    version     = '1.00'
    version_date    = 'October 2022'
    dev_state       = 'Development'
    cmd_desc        = 'Enhanced Sizing and Provisioning'
    banner          = cmd_desc + ': Release ' + version_date
    file_type       = 'esp'

    # Process command line Options
    # -----------------------------------
    #
    ArgParser = OptionParser()
    ArgParser.add_option("-c",         dest="coll_id",     default=".",    type=str,   help="collection id")
    ArgParser.add_option("-v",         dest="verbose",     default=False,              help="verbose")
    ArgParser.add_option("--v",        dest="show_ver",    default=False,     type=str,   help="filter")

    Option, Args = ArgParser.parse_args()
    vCollection    = Option.coll_id
    vVerbose       = Option.verbose
    vVersionDate   = Option.show_ver

    vStartDir = ''
    vDirLoc = ''
    vCollectionDir = ''
    vDatabaseFiles = ''
    vClientId = ''
    vClientName = ''
    acmeConn = ''
    
    # Get connection for MySQL
    acmeConn = getDBConnection()
    
    # Create the entry for sp_Database
    updSpDatabase(acmeConn, vCollection)

    acmeConn.close()