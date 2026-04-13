import os
import csv
import mysql.connector
from mysql.connector import errorcode
from zipfile import ZipFile
import glob
from datetime import datetime

pCollection = "1"
acmeConn = ''
vCursor = ''
vQuery = ''
vClientInfo = ''
vFileSet = ''
pDatabaseId = 0

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

vInsCursor = acmeConn.cursor()
   
for vHostFile in glob.glob("escp*.zip"):
   pDatabaseId = 0
   vFilePart = vHostFile.split("_")
   vHostName = vFilePart[2]
   vDBName = vFilePart[3]
   print(f"before insert ... ", vHostFile, vHostName, vDBName)

   vInsQuery = "insert into sp_database (db_id, db_name, db_shortname, db_filename, db_collection_host, sp_collection_coll_id)   \
              values (%s, %s, %s, %s, %s, %s)"
                  
   vInsCursor.execute(vInsQuery, (pDatabaseId, vDBName, vDBName, vHostFile, vHostName, pCollection,))
   pDatabaseId = vInsCursor.lastrowid
   print(f"after the insert, this is the databaseId: ", pDatabaseId)

   acmeConn.commit()
   vInsCursor.close()

   with ZipFile(vHostFile, 'r') as zip_ref:
      zip_ref.extractall("/tmp/espTempDir")

   escpFileName = glob.glob("/tmp/espTempDir/escp*.csv")
   cpuFileName = glob.glob("/tmp/espTempDir/cpuinfo*.txt")
   print(escpFileName, cpuFileName)
   
   cpuFile = open(cpuFileName[0], 'r')
   cpuLines = cpuFile.readlines()

   cpuType = ''
   vModel = ''

   lineCount = 0
   for line in cpuLines:
      lineCount += 1
      print("Cpu Lines: ", lineCount, " ", line)
      if lineCount == 1: 
         print(line)
         lineSplit = line.split(':')
         print(lineSplit)
         cpuType = lineSplit[1].strip()
      else:
         vModel = line.strip()

   print (cpuType, vModel)
   
   vAppCursor = acmeConn.cursor()
   vAppQuery = "update sp_database set db_host_cpu = %s, db_host_model = %s where db_id = %s;"

   vAppCursor.execute(vAppQuery, (cpuType, vModel, pDatabaseId,))

   acmeConn.commit()
   vAppCursor.close()

   with open(escpFileName[0]) as espCSVFile:
      csv_reader = csv.reader(espCSVFile, delimiter=',')

      is_identity = 1      # indicates we are processing the top of the escp file (identity)
      csvLineCount = 0
      identCount = 0
      metrCount = 0

      for csvRow in csv_reader:
         groupName = csvRow[0].strip()
         metricName = csvRow[1].strip()
         instanceNo = csvRow[2].strip()
         endDate = csvRow[3].strip()
         collValue = csvRow[4].strip()

         if groupName != 'METGROUP':
            if endDate != '':
               collDate = datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%S')
            else: collDate = ''

            if is_identity:
              if groupName == 'CPU':
                 is_identity = 0
                 metrCount += 1
              else: identCount += 1
            else: 
              metrCount += 1

      print(f"Read Complete with Identity Count: ", identCount, " and MetrCount: ", metrCount)

      vFileSet = os.listdir("/tmp/espTempDir")
      for file in vFileSet:
         rmFile = '/tmp/espTempDir'+'/'+file 
         os.remove(rmFile)
