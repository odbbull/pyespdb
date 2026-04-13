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
             and b.mp_metricname = 'OS' and b.mp_metricacronym = 'OSBUSY' and b.mp_instance = 1  \
           group by a.db_id, a.db_name"

vQuery2 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'OS' and b.mp_metricacronym = 'OSBUSY' and b.mp_instance = 2  \
           group by a.db_id, a.db_name"

vQuery3 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'OS' and b.mp_metricacronym = 'OSLOAD' and b.mp_instance = 1  \
           group by a.db_id, a.db_name"

vQuery4 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'OS' and b.mp_metricacronym = 'OSLOAD' and b.mp_instance = 2  \
           group by a.db_id, a.db_name"           
                  
osbusy1_df = pd.read_sql(vQuery1, acmeConn)
osbusy2_df = pd.read_sql(vQuery2, acmeConn)
osload1_df = pd.read_sql(vQuery3, acmeConn)
osload2_df = pd.read_sql(vQuery4, acmeConn)

with pd.ExcelWriter("vanMaxOSMetrics_Prod.xlsx") as writer:
   osbusy1_df.to_excel(writer, sheet_name="osbusy1", index=False)
   osbusy2_df.to_excel(writer, sheet_name="osbusy2", index=False)
   osload1_df.to_excel(writer, sheet_name="osload1", index=False)
   osload2_df.to_excel(writer, sheet_name="osload2", index=False)
