import os
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
import plotly as py
import plotly.express as px
import plotly.graph_objs as go

df = pd.read_excel('/Users/henry.d.tullis/Development/pyespdb/util/vanMaxMetrics.xlsx')

fig = px.scatter(df, y="MBPS", x="storTotal", color="dbId", log_x=True, size="storTotal", 
                 size_max=60, hover_name="dbName", height=600, width=1000, template="simple_white", 
                 color_discrete_sequence=px.colors.qualitative.G10, title="Database Size by Throughput (MBPS)")

fig.update_xaxes(title="Storage Used / Database Size")
fig.update_yaxes(title="Throughput (MBPS)")

fig.show()
