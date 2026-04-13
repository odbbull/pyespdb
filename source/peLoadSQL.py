from optparse		import OptionParser
from os.path		import basename
from sys		import argv
from sys		import exit
import os
import csv
import mysql.connector
from mysql.connector import errorcode
import pandas as pd

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

def getClientCollection(pConn, pCollId):

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
   pFileName = vResult[2]
   pClientId = vResult[0]
   pClientName = vResult[1]

   vCursor.close()

   return pFileName, pClientId, pClientName

def convertTargetDate(pTargetDate):
   
   try:
      vTempString = pTargetDate.split(" ")
      vYear = vTempString[0]
      vQtr = vTempString[1]
   
   except:    
      vYear = ""
      vQtr = ""
      
   return (vYear, vQtr)

def insSqlDatabase(pConn, pCollection, pServerName, pAppServer, pEnviron, pOpStatus, pOpSys, pSqlVersion, 
               pAppLookup, pMecTracked, pTargetDisp, pTargetYear, pTargetQtr, pStageMod):
   
   vInsCursor = pConn.cursor()
   vDatabaseId = 0

   vInsQuery = "insert into sp_sqlDatabase(sq_id, sq_dbName, sq_app_service, sq_environment, sq_opp_status,  \
                   sq_os, sq_sql_version, sq_name_lookup, sq_MEC_tracked, sq_ts_disp, sq_ts_year, sq_ts_qtr, \
                   sq_stage1_mod, sp_collection_coll_id)                                                     \
                 values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
   
   vInsCursor.execute(vInsQuery,(vDatabaseId, pServerName, pAppServer, pEnviron, pOpStatus, pOpSys, 
               pSqlVersion, pAppLookup, pMecTracked, pTargetDisp, pTargetYear, pTargetQtr, pStageMod, pCollection,))

   vDatabaseId = vInsCursor.lastrowid
   
   vInsCursor.close()
   
   pConn.commit()
   return vDatabaseId

def insSqlMetrics(pConn, pSqldbId, pRam, pDiskSpace, pCpuCount, pCoreCount, pLogCpu):

   vMetCursor = pConn.cursor()
   vMetricId = 0

   vMetQuery = "insert into sp_sqlMetrics(sm_id, sm_ram, sm_diskspace, sm_cpu_count, sm_cpu_core,       \
                   sm_logical_cpu, sp_sqldatabase_sq_id)                                                \
                 values (%s, %s, %s, %s, %s, %s, %s)"
 
   vMetCursor.execute(vMetQuery, (vMetricId, pRam, pDiskSpace, pCpuCount, pCoreCount, pLogCpu, pSqldbId,))
   vMetricId = vMetCursor.lastrowid
   
   pConn.commit()
   vMetCursor.close()
   
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
   # Get Collecction directory
   vFileName, vClientName, vClientId = getClientCollection(acmeConn, vCollection)

   vRecordCntr = 0
   
   df = pd.read_excel(vFileName)
   df = df.fillna('')
   
   vTotalRec = len(df.index)
   vTargetDate = ""

   for row in df.itertuples():
      vServerName = row[1].upper()
      vAppServer = row[2]
      vEnviron = row[3]
      vOpStatus = row[4]
      vOpSys = row[5]
      vSqlVersion = row[6]
      vRam = row[7]
      vDiskSpace = row[8]
      vCpuCount = row[9]
      vCoreCount = row[10]
      vLogCpu = row[11]
      vAppLookup = row[12]
      vMecTracked = row[13]
      vTargetDisp = row[14]
      vTargetDate = row[15]
      vStageMod = row[16]

      vRecordCntr += 1
      
      vTargetYear, vTargetQtr = convertTargetDate(vTargetDate)
      
      vSqldbId = insSqlDatabase(acmeConn, vCollection, vServerName, vAppServer, vEnviron, vOpStatus, vOpSys, 
                        vSqlVersion, vAppLookup, vMecTracked, vTargetDisp, vTargetYear, vTargetQtr, vStageMod)
      
      insSqlMetrics(acmeConn, vSqldbId, vRam, vDiskSpace, vCpuCount, vCoreCount, vLogCpu)

      print(f"Processed { vRecordCntr } of { vTotalRec } is this server: { vServerName }")

   acmeConn.close()