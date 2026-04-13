import os
import mysql.connector

vCollection = 1
acmeConn = ''
vCursor = ''
vQuery = ''

acmeConn = mysql.connector.connect(user='acme', password='welcome1',
                                      host='127.0.0.1', database='AcmeAnvil')

vCursor = acmeConn.cursor()
   
vQuery = "select db_id, db_filename from sp_database where sp_collection_coll_id = %s"
                  
vCursor.execute(vQuery, (vCollection,))
vResult = vCursor.fetchall()

for result in vResult:
   print (result)
   vDatabaseId = result[0]
   vFilePath = result[1]

   print (f"ID; ", vDatabaseId, " Path: ", vFilePath)
