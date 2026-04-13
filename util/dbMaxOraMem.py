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
             and b.mp_metricname = 'MEM' and b.mp_metricacronym = 'SGA' and b.mp_instance = 1  \
           group by a.db_id, a.db_name"

vQuery2 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'MEM' and b.mp_metricacronym = 'SGA' and b.mp_instance = 2  \
           group by a.db_id, a.db_name"

vQuery3 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'MEM' and b.mp_metricacronym = 'PGA' and b.mp_instance = 1  \
           group by a.db_id, a.db_name"

vQuery4 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'MEM' and b.mp_metricacronym = 'PGA' and b.mp_instance = 2  \
           group by a.db_id, a.db_name"           
                  
sga1_df = pd.read_sql(vQuery1, acmeConn)
sga2_df = pd.read_sql(vQuery2, acmeConn)
pga1_df = pd.read_sql(vQuery3, acmeConn)
pga2_df = pd.read_sql(vQuery4, acmeConn)

with pd.ExcelWriter("vanMaxMemory_Prod.xlsx") as writer:
   sga1_df.to_excel(writer, sheet_name="sga 1", index=False)
   sga2_df.to_excel(writer, sheet_name="sga 2", index=False)
   pga1_df.to_excel(writer, sheet_name="pga 1", index=False)
   pga2_df.to_excel(writer, sheet_name="pga 2", index=False)
