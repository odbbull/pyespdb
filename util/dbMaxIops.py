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
             and b.mp_metricname = 'IOPS' and b.mp_metricacronym = 'RREQS' and b.mp_instance = 1  \
           group by a.db_id, a.db_name"

vQuery2 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'IOPS' and b.mp_metricacronym = 'WREDO' and b.mp_instance = 1  \
           group by a.db_id, a.db_name"

vQuery3 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id  and a.sp_collection_coll_id = 2                \
             and b.mp_metricname = 'IOPS' and b.mp_metricacronym = 'WREQS' and b.mp_instance = 1  \
           group by a.db_id, a.db_name"

vQuery4 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id  and a.sp_collection_coll_id = 2                \
             and b.mp_metricname = 'IOPS' and b.mp_metricacronym = 'RREQS' and b.mp_instance = 2  \
           group by a.db_id, a.db_name"

vQuery5 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id and a.sp_collection_coll_id = 2                 \
             and b.mp_metricname = 'IOPS' and b.mp_metricacronym = 'WREDO' and b.mp_instance = 2  \
           group by a.db_id, a.db_name"

vQuery6 = "select a.db_id, a.db_name, max(cast(b.mp_plotvalue as decimal(10.2))) sessions      \
            from sp_database a, sp_metricplot b                                                \
           where a.db_id = b.sp_database_db_id  and a.sp_collection_coll_id = 2                \
             and b.mp_metricname = 'IOPS' and b.mp_metricacronym = 'WREQS' and b.mp_instance = 2  \
           group by a.db_id, a.db_name"

 
                  
rreqs1_df = pd.read_sql(vQuery1, acmeConn)
wredo1_df = pd.read_sql(vQuery2, acmeConn)
wreqs1_df = pd.read_sql(vQuery3, acmeConn)
rreqs2_df = pd.read_sql(vQuery4, acmeConn)
wredo2_df = pd.read_sql(vQuery5, acmeConn)
wreqs2_df = pd.read_sql(vQuery6, acmeConn)


with pd.ExcelWriter("vanMaxIops.xlsx") as writer:
   rreqs1_df.to_excel(writer, sheet_name="rreqs1", index=False)
   wredo1_df.to_excel(writer, sheet_name="wredo1", index=False)
   wreqs1_df.to_excel(writer, sheet_name="wreqs1", index=False)
   rreqs2_df.to_excel(writer, sheet_name="rreqs2", index=False)
   wredo2_df.to_excel(writer, sheet_name="wredo2", index=False)
   wreqs2_df.to_excel(writer, sheet_name="wreqs2", index=False)

