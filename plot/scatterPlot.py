import os
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
import plotly as py
import plotly.express as px
import plotly.graph_objs as go

try:
   acmeConn = mysql.connector.connect(user='acme', password='welcome1',
                                      host='127.0.0.1', database='AcmeAnvil')
except mysql.connector.Error as err:
   if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print(f"Something is wrong with username and password")
   elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print(f"Database does not exist")
   else:
      print(err)

vQuery = "select db.db_name dbName1, format(max(cast(mp_plotvalue as decimal(10,2))),2) pvDisk   \
            from sp_database db, sp_metricplot mp where db.db_id = mp.sp_database_db_id         \
             and mp.mp_metricname = 'DISK' and mp.mp_metricAcronym = 'PERM'                     \
           group by db.db_name;"

vQuery1 = "select db.db_name dbName2, max(cast(mp.mp_plotvalue as decimal(10,2))) pvSession      \
             from sp_database db, sp_metricplot mp                                              \
            where db.db_id = mp.sp_database_db_id and mp.mp_metricname = 'CPU'                  \
              and mp.mp_metricAcronym = 'CPU' group by db.db_name;"

cpuPlot1 = pd.read_sql_query(vQuery, acmeConn)
cpuPlot2 = pd.read_sql_query(vQuery1, acmeConn)

px.scatter(cpuPlot1, x="dbName1", y="pvDisk", color="dbName1", log_x=True, size="pvDisk",
            size_max=60, hover_name="dbName1", height=600, width=1000, template="simple_white",
            color_discrete_sequence=px.colors.qualitative.G10, title="Sessions by Storage")

fig = go.Figure()

fig.add_trace(go.Scatter(x=cpuPlot1.dbName1, y=cpuPlot1.pvDisk, mode='lines', name='', line_color='blue'))
fig.add_trace(go.Scatter(x=cpuPlot2.dbName2, y=cpuPlot2.pvSession, mode='lines', name='Instance 2', line_color='red'))

fig.update_traces(marker_line_width=2, marker_size=10)

fig.show()
