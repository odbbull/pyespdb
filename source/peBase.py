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
import zipfile
from zipfile import ZipFile
import glob

###
## Application Imports
###
### from dbClassAnvil   import *

CONST_TEMPDIR = "/tmp/espTempDir"

def getDirectoryNames(pCollDir):
   vDirSet = os.listdir(pCollDir)
   
   return vDirSet  
    
def getFileNames(pStartDir, pFileSet):
   vStartDir    = ''
##
## Check to see if the directory is available or if we need to get the directory
##
   if pStartDir == ".":
       vStartDir = os.getcwd()
   else:
       vStartDir = pStartDir

   pFileSet = os.listdir(vStartDir) 
    
def getDBConnection():

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
   else:
      return (pyespConn)
  
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

def getCollectionDirs(pHostDir):
   vHostPath = pHostDir + '/' + 'escp*.zip'
   vDatabaseFiles = glob.glob(vHostPath)

   return vDatabaseFiles
   
def insSpDatabase(pConn, pCollection, pDatabaseId, pHostFile):
   vFilePart = vHostFile.split("_")
   vHostName = vFilePart[2]
   vDBName = vFilePart[3]
   
   vInsCursor = pConn.cursor()
   
   vInsQuery = "insert into sp_database (db_id, db_name, db_shortname, db_filename, db_collection_host, sp_collection_coll_id)   \
                  values (%s, %s, %s, %s, %s, %s)"
                  
   vInsCursor.execute(vInsQuery, (pDatabaseId, vDBName, vDBName, vHostFile, vHostName, pCollection,))
   pDatabaseId = vInsCursor.lastrowid
   
   vInsCursor.close()

   return pDatabaseId

def unzHostFile(pHostFile):
   with ZipFile(pHostFile,'r') as zip_ref:
      zip_ref.extractall(CONST_TEMPDIR)

def readCpuDetails(pCpuFileName, pCpuType, pServerModel):
   cpuFile = open(pCpuFileName[0], 'r')
   cpuLines = cpuFile.readlines()
   
   firstLine = 1
   for line in cpuLines:
      if firstLine:
         lineSplit = line.split(':')
         pCpuType = lineSplit[1].strip()
         firstLine = 0
      else: pServerModel = line.strip()

   return pCpuType, pServerModel

def loadCpuDetails(pConn, pDatabaseId, pCpuType, pServerModel):
   vCursor = pConn.cursor()
   vQuery = "update sp_database set db_host_cpu = %s, db_host_model = %s where db_id = %s;"
   
   vCursor.execute(vQuery, (pCpuType, pServerModel, pDatabaseId))

   pConn.commit()
   vCursor.close()
   
def procEscpDetails(pConn, pDatabaseId, pFileName):

   vIdenQuery = 'insert into sp_DbIdentity                           \
                   (iden_id, iden_metric, iden_acronym, iden_instance, iden_metricdate, iden_metricvalue, sp_database_db_id) \
                  values (%s, %s, %s, %s, %s, %s, %s) '

   vMetrQuery = 'insert into sp_DbMetric                           \
                   (metr_id, metr_metric, metr_acronym, metr_instance, metr_metricdate, metr_metricvalue, sp_database_db_id) \
                  values (%s, %s, %s, %s, %s, %s, %s) '

   vCursor = pConn.cursor()

   with open(pFileName[0]) as espCsvFile:
      csv_reader = csv.reader(espCsvFile, delimiter=',')
      
      vIsIdentity = 1           # indicates we are processing the top of the escp file (identity)
      vLineCounter = 0
      for csvRow in csv_reader:
         vLineCounter += 1
         vMetricId = 0
         groupName = csvRow[0].strip()
         metricName = csvRow[1].strip()
         instanceNo = csvRow[2].strip()
         if instanceNo == '':
            instanceNo = 1
         endDate = csvRow[3].strip()
         collValue = csvRow[4].strip()
         
         if groupName != 'METGROUP':
            if endDate != '':
               collDate = datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%S')
            else: collDate = datetime.today()
            
            if vIsIdentity:
               if groupName == 'CPU':
                  vIsIdentity = 0
                  vCursor.execute(vMetrQuery, (vMetricId, groupName, metricName, instanceNo, collDate, collValue, pDatabaseId,))
               else: 
                  vCursor.execute(vIdenQuery, (vMetricId, groupName, metricName, instanceNo, collDate, collValue, pDatabaseId,))
            else:
               vCursor.execute(vMetrQuery, (vMetricId, groupName, metricName, instanceNo, collDate, collValue, pDatabaseId,))

      print(f"File: ", pFileName, " processed ", vLineCounter, " lines")

   pConn.commit()
   vCursor.close()
   espCsvFile.close()

def clearTempDir():

   vFileSet = os.listdir(CONST_TEMPDIR)
   for file in vFileSet:
      rmFile = CONST_TEMPDIR + '/' + file
      os.remove(rmFile)

# ----------------------
# ---- Main Program
# ----------------------

if (__name__ == '__main__'):
    cmd         = basename(argv[0])
    version     = '1.00'
    version_date    = 'May 2025'
    dev_state       = 'Development'
    cmd_desc        = 'Python Enkitec Sizing and Provisioning'
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
    pyespConn = ''
    
    print("before the start of the connection")
    #Enhanced Get connection for MySQL
    pyespConn = getDBConnection()
    print("after the start of the connection")
    # Get Collecction directory
    vCollectionDir, vClientName, vClientId = getClientCollection(pyespConn, vCollection, vCollectionDir, vClientName, vClientId) 
    print("Collection Directory: ", vCollectionDir)
    
    vDirSet = getDirectoryNames(vCollectionDir)
    print("Collection Directories: ", vDirSet)

    for vDirLoc in vDirSet:
       print("Inside for loop for vDirLoc: ", vDirLoc)
    
       vHostDir = vCollectionDir + "/" + vDirLoc                  # Get the extended directory location
          
    # Get "directories" inside the Collection Directory
       vDatabaseFiles = getCollectionDirs(vHostDir)
       print("Database Files: ", vDatabaseFiles)   

    # Establish Host Name / Database Name - insert into spDatabase
       for vHostFile in vDatabaseFiles:

    # Create the entry for sp_Database
          vDatabaseId = 0
          vDatabaseId = insSpDatabase(pyespConn, vCollection, vDatabaseId, vHostFile)
          
    # Unzip the Host File into a temporary location for processing
          unzHostFile(vHostFile)    

    # Read collection files
          escpFileSearch = CONST_TEMPDIR + '/' + 'escp*.csv'
          escpFileName = glob.glob(escpFileSearch)
          cpuFileSearch = CONST_TEMPDIR + '/' + 'cpuinfo*.txt'
          cpuFileName = glob.glob(cpuFileSearch)
          
    # Process the CPU File and Update the sp_Database Entry
          if cpuFileName:
             vCpuType = ''
             vServerModel = ''
             vCpuType, vServerModel = readCpuDetails(cpuFileName, vCpuType, vServerModel)
             loadCpuDetails(pyespConn, vDatabaseId, vCpuType, vServerModel)

    # Establish the details for the dbIdentity and dbMetric
          if escpFileName:
             procEscpDetails(pyespConn, vDatabaseId, escpFileName)

    # Clear the temporary location and prepare for the next file
          clearTempDir()
    
    # Rename the file to .zipO to indicate it has been changed - make sure to have the directory
          renSourceFile = vHostFile
          renTargetFile = vHostFile + 'O' 
          os.rename(renSourceFile, renTargetFile)
