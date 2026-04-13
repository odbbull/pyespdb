import os
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
import plotly as py
import plotly.express as px
import plotly.graph_objs as go

df = pd.read_excel('/Users/henry.d.tullis/Development/pyespdb/util/vanMaxMetrics.xlsx')

fig = px.scatter(df, y="Sessions", x="MBPS", color="dbId", log_x=True, size="MBPS", 
                 size_max=60, hover_name="dbName", height=600, width=1000, template="simple_white", 
                 color_discrete_sequence=px.colors.qualitative.G10, title="Throughput (MBPS) by Sessions")

fig.update_xaxes(title="Throughput (MBPS)")
fig.update_yaxes(title="Sessions on CPU")

fig.show()
