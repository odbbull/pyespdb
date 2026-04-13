import os
import sys
from optparse       import OptionParser
from os.path        import basename
from sys            import argv
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
import plotly as py
import plotly.express as px
import plotly.graph_objs as go

def getConnection(pConn):
   try:
      pConn = mysql.connector.connect(user='acme', password='welcome1',
                                      host='127.0.0.1', database='AcmeAnvil')
   except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
         print(f"Something is wrong with username and password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
         print(f"Database does not exist")
      else:
         print(err)

   return pConn

def genQueryText(pDbId, pMetric, pAcronym, pInstance):

   pQuery = "select mp_plotdate pd1, cast(mp_plotvalue as decimal(10,2)) pv1 from sp_metricplot    \
              where mp_metricName = '" + pMetric + "' and mp_metricAcronym = '" + pAcronym +          \
              "' and mp_instance = " + pInstance + " and sp_database_db_id = " + pDbId + ";"
   
   hdrQuery = "select db_name from sp_database where db_id = " + pDbId + ";"

   return pQuery, hdrQuery

def getDatabaseName(pConn, pQuery):

    nmCursor = pConn.cursor()
    nmCursor.execute(pQuery)

    nameVal = nmCursor.fetchone()

    return nameVal[0]

if (__name__ == '__main__'):
    cmd         = basename(argv[0])
    version     = '1.00'
    version_date    = 'October 2022'
    dev_state       = 'Development'
    cmd_desc        = 'Enhanced Sizing and Provisioning'
    banner          = cmd_desc + ': Release ' + version_date
    file_type       = 'esp'

    # Process command line Options
    # -----------------------------------
    #
    ArgParser = OptionParser()
    ArgParser.add_option("-d",         dest="dbId",        default=".",    type=str,   help="Database id")
    ArgParser.add_option("-m",         dest="vMetric",     default=".",    type=str,   help="Metric Name")
    ArgParser.add_option("-a",         dest="vAcronym",    default=".",    type=str,   help="Acronym Name")
    ArgParser.add_option("-i",         dest="vInstance",   default="1",    type=str,   help="Instance ID")
    ArgParser.add_option("-c",         dest="vColor",      default="b",    type=str,   help="Line Color")
    ArgParser.add_option("-v",         dest="verbose",     default=False,              help="verbose")
    ArgParser.add_option("--v",        dest="show_ver",    default=False,     type=str,   help="filter")

    Option, Args = ArgParser.parse_args()
    vDbId          = Option.dbId
    vMetric        = Option.vMetric
    vAcronym       = Option.vAcronym
    vInstance      = Option.vInstance
    vColor         = Option.vColor
    vVerbose       = Option.verbose
    vVersionDate   = Option.show_ver
    
    acmeConn = ''
    if not vInstance:
       vInstance = 1

    if vColor.upper() == "B":
       vColor = "blue"
    elif vColor.upper() == "G":
       vColor = "green"
    elif vColor.upper() == "R":
       vColor = "red"
    elif vColor.upper() == "Y":
       vColor = "goldenrod"
    else:
       vColor = "blue"
       

    acmeConn = getConnection(acmeConn)
    
    vQuery, hdrQuery = genQueryText(vDbId, vMetric, vAcronym, vInstance)
    
    cpuPlot1 = pd.read_sql_query(vQuery, acmeConn, parse_dates=['pd1'])

    vName = getDatabaseName(acmeConn, hdrQuery)
    if vName == 'CPU':
       vTitleName = 'Sessions on CPU for ' + vName + ' Instance: ' + vInstance
    else:
       vTitleName = vMetric + ' Details of ' + vName + ' Instance: ' + vInstance

    fig = px.scatter(title=vTitleName)

# fig = go.Figure()

    fig.add_trace(go.Scatter(x=cpuPlot1.pd1, y=cpuPlot1.pv1, mode='lines', name=vAcronym, line_color=vColor))

# fig.update_traces(marker_line_width=2, marker_size=10)

    if vAcronym == 'CPU':
       vTitle = "Sessions on CPU"
    else:
       vTitle = vMetric + " " + vAcronym + " Metrics"
    fig.update_xaxes(title="Collection Date")
    fig.update_yaxes(title=vTitle)

    fig.show()
