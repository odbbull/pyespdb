import os
import mysql.connector
from mysql.connector import errorcode

vQuery = ''
vClientInfo = ''

acmeConn = mysql.connector.connect(user='acme', password='welcome1',
                                      host='127.0.0.1', database='AcmeAnvil')
vCursor = acmeConn.cursor(dictionary=True)

vQuery = "select cat_name, cat_acronym from sp_category where is_static_fg = 0 and is_active_fg = 1;"

vCursor.execute(vQuery)
# vCatInfo = vCursor.fetchall()

# for result in vCatInfo:
#    vCategory = catDict([ k[0], k[1:]) for k in rows]

for row in vCursor:
   vCatName = row['cat_name']
   vCatAcronym = row['cat_acronym']
   print(f"Name is: ", vCatName, " Acronym is ", vCatAcronym)

vCursor.close()
acmeConn.close()
