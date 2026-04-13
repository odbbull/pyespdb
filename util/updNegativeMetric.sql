import os
import mysql.connector

vCollection = 1
acmeConn = ''
vCursor = ''
vQuery = ''

acmeConn = mysql.connector.connect(user='acme', password='welcome1',
                                      host='127.0.0.1', database='AcmeAnvil')

vCursor = acmeConn.cursor()
   
vQuery = "select mp_id, cast(mp_plotvalue as decimal(15,2)) from sp_metricplot;"
                  
vCursor.execute(vQuery)
vResult = vCursor.fetchall()

holdValue = 0

for result in vResult:
   vRowId = result[0]
   vplotValue = result[1]

   print (f"ID; ", vDatabaseId, " Path: ", vFilePath)
