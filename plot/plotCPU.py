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

vQuery = "select mp_plotdate pd1, cast(mp_plotvalue as decimal(10,2)) pv1 from sp_metricplot    \
           where mp_metricName = 'CPU' and mp_metricAcronym = 'CPU' and mp_instance = 1            \
             and sp_database_db_id = 359;"

vQuery1 = "select mp_plotdate pd2, cast(mp_plotvalue as decimal(10,2)) pv2 from sp_metricplot    \
           where mp_metricName = 'CPU' and mp_metricAcronym = 'CPU' and mp_instance = 2            \
             and sp_database_db_id = 359;"

cpuPlot1 = pd.read_sql_query(vQuery, acmeConn, parse_dates=['pd1'])
cpuPlot2 = pd.read_sql_query(vQuery1, acmeConn, parse_dates=['pd2'])

px.line(cpuPlot1, x='pd1', y='pv1', labels={'x':'Date', 'y':'Sessions on CPU'})

fig = go.Figure()

fig.add_trace(go.Scatter(x=cpuPlot1.pd1, y=cpuPlot1.pv1, mode='lines', name='Instance 1', line_color='blue'))
fig.add_trace(go.Scatter(x=cpuPlot2.pd2, y=cpuPlot2.pv2, mode='lines', name='Instance 2', line_color='red'))

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
