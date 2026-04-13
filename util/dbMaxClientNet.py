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
   
vQuery1 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id  and a.sp_collection_coll_id = 2                \
             and b.mp_metricname = 'NETW' and b.mp_metricacronym = 'FROMCLIENT' and b.mp_instance = 1  \
           group by a.db_id, a.db_name"

vQuery2 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'NETW' and b.mp_metricacronym = 'TOCLIENT' and b.mp_instance = 1  \
           group by a.db_id, a.db_name"

vQuery3 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'NETW' and b.mp_metricacronym = 'FROMCLIENT' and b.mp_instance = 2  \
           group by a.db_id, a.db_name"

vQuery4 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'NETW' and b.mp_metricacronym = 'TOCLIENT' and b.mp_instance = 2  \
           group by a.db_id, a.db_name"           
                  
fmclnt1_df = pd.read_sql(vQuery1, acmeConn)
toclnt1_df = pd.read_sql(vQuery2, acmeConn)
fmclnt2_df = pd.read_sql(vQuery3, acmeConn)
toclnt2_df = pd.read_sql(vQuery4, acmeConn)

with pd.ExcelWriter("vanMaxClientNet_Prod.xlsx") as writer:
   fmclnt1_df.to_excel(writer, sheet_name="fromclient1", index=False)
   toclnt1_df.to_excel(writer, sheet_name="toclient1", index=False)
   fmclnt2_df.to_excel(writer, sheet_name="fromclient2", index=False)
   toclnt2_df.to_excel(writer, sheet_name="toclient2", index=False)
