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

CONST_INTERVAL = 3600

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

def genCategoryDict(pConn):
   
   vGetCursor = pConn.cursor(dictionary=True)
   
   vGetQuery = "select cat_name, cat_acronym, gen_summary, add_interval_fg,     \
                       cat_yaxis_unit, cat_yaxis_divisor                         \
                  from sp_category where is_active_fg = 1 and gen_summary = 1;"
   
   vGetCursor.execute(vGetQuery)
   
   return vGetCursor

def loadSummaryMetrics(pConn, pDatabaseId, pCatName, pCatAcronym):

   vCursor = pConn.cursor()
   
   vGetQuery = "select mp_metricName, mp_metricacronym, mp_instance,      \
                  format(max(cast(mp_plotvalue as decimal(10,2))),2), format(avg(cast(mp_plotvalue as decimal(10,2))),2)   \
                  from sp_metricplot where sp_database_db_id = %s and mp_metricname = %s and mp_metricacronym = %s  \
                 group by mp_metricname, mp_metricacronym, mp_instance order by mp_instance;"
               
   vInsQuery = "insert into sp_dbMetric_Summ(ms_metric, ms_acronym, ms_instance, ms_maxvalue, ms_avgvalue,    \
                   sp_database_db_id) values (%s, %s, %s, %s, %s, %s);"

   vCursor.execute(vGetQuery, (pDatabaseId, pCatName, pCatAcronym,))
   
   vMetrInfo = vCursor.fetchall()
   for mResult in vMetrInfo:
      vInstance = mResult[2]
      vMaxString = mResult[3]
      vAvgString = mResult[4]
      vMetricMax = float(vMaxString.replace(",",""))
      vMetricAvg = float(vAvgString.replace(",",""))

      vCursor.execute(vInsQuery, (pCatName, pCatAcronym, vInstance, f'{vMetricMax:.3f}', f'{vMetricAvg:.3f}', pDatabaseId,))

   pConn.commit()
   vCursor.close()

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

    vDatabaseId = ''
    acmeConn = ''
    vDbCursor = ''
    vCategoryDict = {}

  # Get connection for MySQL
    dictConn = getDBConnection()
    acmeConn = getDBConnection() 

    vDbCursor = acmeConn.cursor()
    vGetDbQuery = "select db_id, db_name from sp_database where sp_collection_coll_id = %s"
    vDbCursor.execute(vGetDbQuery, (vCollection,))

    vGetResult = vDbCursor.fetchall()
   
    for result in vGetResult:
       vDatabaseId = result[0]
       vDbName = result[1]

       print(f"Processing Categories for Database: ", vDatabaseId, vDbName)

  # Establish the category dictionary - 
       vCategoryDict = genCategoryDict(dictConn)
    
       for dictRow in vCategoryDict:

          if dictRow['gen_summary']:
             loadSummaryMetrics(acmeConn, vDatabaseId, dictRow['cat_name'], dictRow['cat_acronym'])
    
       vCategoryDict.close()
        
    acmeConn.close()
    dictConn.close()
