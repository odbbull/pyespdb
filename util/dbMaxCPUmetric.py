import os
import mysql.connector
import pandas as pd

vCollection = 1
acmeConn = ''
vCursor = ''
vQuery1 = ''
vQuery2 = ''

acmeConn = mysql.connector.connect(user='acme', password='welcome1',
                                      host='127.0.0.1', database='AcmeAnvil')

vCursor = acmeConn.cursor()
   
vQuery1 = "select a.db_id, a.db_name,      \
             DATE(b.mp_plotdate) as DATE, max(cast(b.mp_plotvalue as decimal(10.2))) sessions  \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id  and a.sp_collection_coll_id = 2                \
             and b.mp_metricname = 'CPU' and b.mp_metricacronym = 'CPU' and b.mp_instance = 1  \
           group by a.db_id, a.db_name, DATE(b.mp_plotdate)"

vQuery2 = "select a.db_id, a.db_name,      \
             DATE(b.mp_plotdate) as DATE, max(cast(b.mp_plotvalue as decimal(10.2))) sessions  \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'CPU' and b.mp_metricacronym = 'CPU' and b.mp_instance = 2  \
           group by a.db_id, a.db_name, DATE(b.mp_plotdate)"
                  
inst1_df = pd.read_sql(vQuery1, acmeConn)
inst2_df = pd.read_sql(vQuery2, acmeConn)

with pd.ExcelWriter("vanMaxSession.xlsx") as writer:
   inst1_df.to_excel(writer, sheet_name="instance1", index=False)
   inst2_df.to_excel(writer, sheet_name="instance2", index=False)
