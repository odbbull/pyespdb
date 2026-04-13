from optparse       import OptionParser
import os
from sys            import argv
from os.path import basename
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime

pCollection = "1"
acmeConn = ''
vCursor = ''
vQuery = ''
vClientInfo = ''
vFileSet = ''
pDatabaseId = 0

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
   
def loadExaFrame(pConn, pHostName, pModel):
   
   vFrameId = 0
   vFrame = pHostName[0:10]
   vLocation = pHostName[0:3]
   
   vTemp = pModel.split()
   vExaModel = vTemp[2]
   
   vGetCursor = pConn.cursor()
   vInsCursor = pConn.cursor()
   
   vFrameQuery = "select fr_id from sp_ExaFrame where fr_name = %s;"

   vInsQuery = "insert into sp_ExaFrame (fr_id, fr_name, fr_location, fr_model, is_active_fg)   \
              values (%s, %s, %s, %s, %s)"
                  
   vGetCursor.execute(vFrameQuery, (vFrame,))
   vRow = vGetCursor.fetchone()
   if not vRow:
      vInsCursor.execute(vInsQuery, (vFrameId, vFrame, vLocation, vExaModel, '1',))
      vFrameId = vInsCursor.lastrowid
   else:
      vFrameId = vRow[0]

   acmeConn.commit()
   vGetCursor.close()
   vInsCursor.close()
   
   return vFrameId

def loadDbHost(pConn, pFrameId, pInstance, pInstHost):
   
   vTemp = pInstHost.split()
   vExaHost = vTemp[0]
   vHostId = 0
   vLocation = vExaHost[0:3]
   
   vGetCursor = pConn.cursor()
   vInsCursor = pConn.cursor()
   
   vHostQuery = "select hs_id from sp_host where hs_name = %s and hs_instance = %s;"

   vInsQuery = "insert into sp_host (hs_id, hs_name, hs_location, hs_instance,        \
                   is_active_fg, sp_exaframe_fr_id)   \
              values (%s, %s, %s, %s, %s, %s);"
                  
   vGetCursor.execute(vHostQuery, (vExaHost, pInstance,))
   vRow = vGetCursor.fetchone()
   if not vRow:
      vInsCursor.execute(vInsQuery, (vHostId, vExaHost, vLocation, vInstance, '1', vFrameId,))
      vHostId = vInsCursor.lastrowid
   else:
      vHostId = vRow[0]

   pConn.commit()
   vGetCursor.close()
   vInsCursor.close()
   
   return vHostId
   
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

    acmeConn = ''
    vInstance = 0
    
    # Get connection for MySQL
    acmeConn = getDBConnection()
    
    dbQuery = "select db.db_id, db.db_host_model, db.db_collection_host,             \
                  id.iden_instance, id.iden_metricvalue                              \
                from sp_database db, sp_dbidentity id                                \
               where id.sp_database_db_id = db.db_id and db.sp_host_hs_id is null     \
                 and id.iden_metric = 'INSTANCE' and id.iden_acronym = 'HOST_NAME';"
    
    dbCursor = acmeConn.cursor()
    
    dbCursor.execute(dbQuery)
   
    dbFrameLoc = dbCursor.fetchall()
    for mResult in dbFrameLoc:
       vFrameId = 0
       vDatabaseId = mResult[0]
       vModel = mResult[1]
       vCollHost = mResult[2]
       vInstance = mResult[3]
       vInstHost = mResult[4]
       
       vFrameId = loadExaFrame(acmeConn, vCollHost, vModel)
       
       vHostId = loadDbHost(acmeConn, vFrameId, vInstance, vInstHost)

       updQuery = "update sp_database set sp_host_hs_id = %s where db_id = %s;"
       updCursor = acmeConn.cursor()
       updCursor.execute(updQuery,(vHostId, vDatabaseId,))
    
       acmeConn.commit()
       updCursor.close()

    dbCursor.close()