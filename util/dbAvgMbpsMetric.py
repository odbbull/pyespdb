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
             DATE(b.mp_plotdate) as DATE, avg(cast(b.mp_plotvalue as decimal(10.2))) sessions  \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id  and a.sp_collection_coll_id = 2                \
             and b.mp_metricname = 'MBPS' and b.mp_metricacronym = 'RBYTES' and b.mp_instance = 1  \
           group by a.db_id, a.db_name, DATE(b.mp_plotdate)"

vQuery2 = "select a.db_id, a.db_name,      \
             DATE(b.mp_plotdate) as DATE, avg(cast(b.mp_plotvalue as decimal(10.2))) sessions  \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'MBPS' and b.mp_metricacronym = 'RBYTES' and b.mp_instance = 2  \
           group by a.db_id, a.db_name, DATE(b.mp_plotdate)"

vQuery3 = "select a.db_id, a.db_name,      \
             DATE(b.mp_plotdate) as DATE, avg(cast(b.mp_plotvalue as decimal(10.2))) sessions  \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id  and a.sp_collection_coll_id = 2                \
             and b.mp_metricname = 'MBPS' and b.mp_metricacronym = 'WBYTES' and b.mp_instance = 1  \
           group by a.db_id, a.db_name, DATE(b.mp_plotdate)"

vQuery4 = "select a.db_id, a.db_name,      \
             DATE(b.mp_plotdate) as DATE, avg(cast(b.mp_plotvalue as decimal(10.2))) sessions  \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'MBPS' and b.mp_metricacronym = 'WBYTES' and b.mp_instance = 2  \
           group by a.db_id, a.db_name, DATE(b.mp_plotdate)"           
                  
rbyte1_df = pd.read_sql(vQuery1, acmeConn)
rbyte2_df = pd.read_sql(vQuery2, acmeConn)
wbyte1_df = pd.read_sql(vQuery3, acmeConn)
wbyte2_df = pd.read_sql(vQuery4, acmeConn)

with pd.ExcelWriter("vanAvgMbps.xlsx") as writer:
   rbyte1_df.to_excel(writer, sheet_name="rdinst1", index=False)
   rbyte2_df.to_excel(writer, sheet_name="rdinst2", index=False)
   wbyte1_df.to_excel(writer, sheet_name="wrinst1", index=False)
   wbyte2_df.to_excel(writer, sheet_name="wrinst2", index=False)
