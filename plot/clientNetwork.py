import os
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
import plotly as py
import plotly.express as px
import plotly.graph_objs as go

df = pd.read_excel('/Users/henry.d.tullis/Development/pyespdb/util/vanMaxClientNet_ProdCons.xlsx')

# fig = px.scatter(df, y="Sessions", x="MBPS", color="dbId", log_x=True, size="MBPS", 
#                  size_max=60, hover_name="dbName", height=600, width=1000, template="simple_white", 
#                  color_discrete_sequence=px.colors.qualitative.G10, title="Throughput (MBPS) by Sessions")

fig = px.line(title="Throughput (MBPS) by Sessions")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df.dbName, y=df.fmClient1, mode='lines', name='From Client Inst 1', line_color='blue'))
# fig.add_trace(go.Scatter(x=df.dbName, y=df.toClient1, mode='lines', name='To Client Inst 1', line_color='green'))
fig.add_trace(go.Scatter(x=df.dbName, y=df.fmClient2, mode='lines', name='From Client Inst 2', line_color='red'))
# fig.add_trace(go.Scatter(x=df.dbName, y=df.toClient2, mode='lines', name='To Client Inst 2', line_color='purple'))

fig.update_xaxes(title="Database Name")
fig.update_yaxes(title="Network Traffic (MBPS)")

fig.show()
