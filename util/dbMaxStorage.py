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
             and b.mp_metricname = 'DISK' and b.mp_metricacronym = 'LOG'                       \
           group by a.db_id, a.db_name"

vQuery2 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'DISK' and b.mp_metricacronym = 'TEMP'                      \
           group by a.db_id, a.db_name"

vQuery3 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id  and a.sp_collection_coll_id = 2                \
             and b.mp_metricname = 'DISK' and b.mp_metricacronym = 'UNDO'                      \
           group by a.db_id, a.db_name"

vQuery4 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'DISK' and b.mp_metricacronym = 'PERM'                      \
           group by a.db_id, a.db_name"           
                  
log_df = pd.read_sql(vQuery1, acmeConn)
temp_df = pd.read_sql(vQuery2, acmeConn)
undo_df = pd.read_sql(vQuery3, acmeConn)
perm_df = pd.read_sql(vQuery4, acmeConn)

with pd.ExcelWriter("vanMaxStorage.xlsx") as writer:
   log_df.to_excel(writer, sheet_name="log", index=False)
   temp_df.to_excel(writer, sheet_name="temp", index=False)
   undo_df.to_excel(writer, sheet_name="undo", index=False)
   perm_df.to_excel(writer, sheet_name="perm", index=False)
