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

def genCategoryDict(pConn):
   
   vGetCursor = pConn.cursor(dictionary=True)
   
   vGetQuery = "select cat_name, cat_acronym, is_static_fg, add_interval_fg,     \
                       cat_yaxis_unit, cat_yaxis_divisor                         \
                  from sp_category where is_active_fg = 1;"
   
   vGetCursor.execute(vGetQuery)
   
   return vGetCursor

def loadStaticMetrics(pConn, pDatabaseId, pCatName, pCatAcronym, pAddInterval, pCatYUnit, pCatYdivisor, pAwrInterval):

   vCursor = pConn.cursor()
   
   vGetQuery = "select metr_metric, metr_acronym, metr_instance, metr_metricdate, metr_metricvalue   \
                  from sp_dbmetric where sp_database_db_id = %s and metr_metric = %s and metr_acronym = %s  \
                 order by metr_instance, metr_metricdate;"
               
   vInsQuery = "insert into sp_metricplot (mp_metricname, mp_metricacronym, mp_instance, mp_plotdate, \
                   mp_plotvalue, sp_database_db_id) values (%s, %s, %s, %s, %s, %s);"

   vCursor.execute(vGetQuery, (pDatabaseId, pCatName, pCatAcronym,))
   
   vMetrInfo = vCursor.fetchall()
   for mResult in vMetrInfo:
      vInstance = mResult[2]
      vMetricDate = mResult[3]
      vMetricValue = float(mResult[4])
      vPlotValue = 0.0

      if pAddInterval:
         vPlotValue = vMetricValue/pAwrInterval
      else:
         vPlotValue = vMetricValue

      vPlotValue = vPlotValue / float(pCatYdivisor)

      vCursor.execute(vInsQuery, (pCatName, pCatAcronym, vInstance, vMetricDate, f'{vPlotValue:.3f}', pDatabaseId,))

   pConn.commit()
   vCursor.close()

def loadDynamicMetrics(pConn, pDatabaseId, pCatName, pCatAcronym, pAddInterval, pCatYUnit, pCatYdivisor, pAwrInterval):

   vCursor = pConn.cursor()
   
   vGetQuery = "select metr_metric, metr_acronym, metr_instance, metr_metricdate, metr_metricvalue   \
                  from sp_dbmetric where sp_database_db_id = %s and metr_metric = %s and metr_acronym = %s  \
                 order by metr_instance, metr_metricdate;"
               
   vInsQuery = "insert into sp_metricplot (mp_metricname, mp_metricacronym, mp_instance, mp_plotdate, \
                   mp_plotvalue, sp_database_db_id) values (%s, %s, %s, %s, %s, %s);"

   vCursor.execute(vGetQuery, (pDatabaseId, pCatName, pCatAcronym,))
   vActiveInstance = -1
   vDeltaValue = 0
   
   vMetrInfo = vCursor.fetchall()
   for mResult in vMetrInfo:
      vInstance = mResult[2]
      vMetricDate = mResult[3]
      vMetricValue = float(mResult[4])
      vPlotValue = 0.0

      if vInstance != vActiveInstance:
         vPrevValue = 0
         vActiveInstance = vInstance

      if vPrevValue: 
         if vMetricValue > vPrevValue:
            vDeltaValue = vMetricValue - vPrevValue

         vPrevValue = vMetricValue

         if pAddInterval:
            vPlotValue = vDeltaValue/pAwrInterval
         else:
            vPlotValue = vDeltaValue

         vPlotValue = vPlotValue / float(pCatYdivisor)

         vCursor.execute(vInsQuery, (pCatName, pCatAcronym, vInstance, vMetricDate, f'{vPlotValue:.3f}', pDatabaseId,))
      
      else: vPrevValue = vMetricValue

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
    ArgParser.add_option("-i",         dest="awr_int",     default=3600,   type=int,   help="awr interval")
    ArgParser.add_option("-v",         dest="verbose",     default=False,              help="verbose")
    ArgParser.add_option("--v",        dest="show_ver",    default=False,     type=str,   help="filter")

    Option, Args = ArgParser.parse_args()
    vCollection    = Option.coll_id
    vAwrInterval   = Option.awr_int
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

          if dictRow['is_static_fg']:
             loadStaticMetrics(acmeConn, vDatabaseId, dictRow['cat_name'], dictRow['cat_acronym'], dictRow['add_interval_fg'],
                 dictRow['cat_yaxis_unit'], dictRow['cat_yaxis_divisor'], vAwrInterval)
          else:
             loadDynamicMetrics(acmeConn, vDatabaseId, dictRow['cat_name'], dictRow['cat_acronym'], dictRow['add_interval_fg'],
                 dictRow['cat_yaxis_unit'], dictRow['cat_yaxis_divisor'], vAwrInterval)        
    
       vCategoryDict.close()
        
    acmeConn.close()
    dictConn.close()
