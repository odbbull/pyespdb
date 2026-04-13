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

vQuery = "select db.db_name dbName1, max(cast(mp.mp_plotvalue as decimal(10,2))) pv1Session      \
             from sp_database db, sp_metricplot mp                                              \
            where db.db_id = mp.sp_database_db_id and mp.mp_metricname = 'CPU'                  \
              and mp.mp_metricAcronym = 'CPU' and mp.mp_instance = 1 group by db.db_name;"

vQuery1 = "select db.db_name dbName2, max(cast(mp.mp_plotvalue as decimal(10,2))) pv2Session      \
             from sp_database db, sp_metricplot mp                                              \
            where db.db_id = mp.sp_database_db_id and mp.mp_metricname = 'CPU'                  \
              and mp.mp_metricAcronym = 'CPU' and mp.mp_instance = 2 group by db.db_name;"

cpuPlot1 = pd.read_sql_query(vQuery, acmeConn)
cpuPlot2 = pd.read_sql_query(vQuery1, acmeConn)

px.line(cpuPlot1, x='dbName1', y='pv1Session', labels={'x':'Date', 'y':'Sessions on CPU'})

fig = go.Figure()

fig.add_trace(go.Scatter(x=cpuPlot1.dbName1, y=cpuPlot1.pv1Session, mode='lines', name='Instance 1', line_color='blue'))
fig.add_trace(go.Scatter(x=cpuPlot2.dbName2, y=cpuPlot2.pv2Session, mode='lines', name='Instance 2', line_color='red'))

fig.update_layout(
   xaxis=dict(
      showline=True,
      showgrid=False,
      showticklabels=True,
      linecolor='black',
      linewidth=2,
      ticks='outside',
      tickfont=dict(
         family='Arial', 
         size=12,
         color='black',
      ),
   ),
   yaxis=dict(
      showline=True,
      showgrid=False,
      showticklabels=True,
      linecolor='black',
      linewidth=2,
      ticks='outside',
      tickfont=dict(
         family='Arial', 
         size=12,
         color='black',
      ),
    ),
    autosize=True,
)
fig.show()
