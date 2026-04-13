import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import psycopg2
import os
from contextlib import contextmanager

def connect_postgres_db():
    """Connect to PostgreSQL Database"""
    try:
       # Connection to PostgreSQL database
       connection = psycopg2.connect(
          host='localhost',
          database='pyespdb',
          user='htullis'
       )

       print("Successfully connected to PostgreSQL Database")
       return connection

    except psycopg2.Error as error:
       print(f"Error connecting to PostgreSQL Database: {error}")
       return None

def getSplashStats():
    """Return counts of clients, projects, collections, hosts, and databases."""
    conn = connect_postgres_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            (SELECT COUNT(*) FROM sp_client)     AS num_clients,
            (SELECT COUNT(*) FROM sp_project)    AS num_projects,
            (SELECT COUNT(*) FROM sp_collection) AS num_collections,
            (SELECT COUNT(*) FROM sp_host)       AS num_hosts,
            (SELECT COUNT(*) FROM sp_database)   AS num_databases
    """)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return {
        "Clients":     int(row[0]),
        "Projects":    int(row[1]),
        "Collections": int(row[2]),
        "Hosts":       int(row[3]),
        "Databases":   int(row[4]),
    }

def getCollectionSummary():

## Retrieve connection string

    conn = connect_postgres_db()
    
    collCursor = conn.cursor()
    
    collCursor.execute("""
        select distinct sp_collection_coll_id,
               coll_name,
               cl_name,
               pr_name,
               count(db_id)
          from sp_database,
               sp_collection,
               sp_project,
               sp_client
         where sp_collection_coll_id = coll_id
           and sp_project_pr_id = pr_id
           and sp_client_cl_id = cl_id
      group by cl_name, pr_name, sp_collection_coll_id, coll_name
      order by 1;
            """)
    
    rows = collCursor.fetchall()
    
    columns = [col[0] for col in collCursor.description]
    
    print(f"Column names: {columns}")
    print(f"Total rows: {len(rows)}")
    
    for row in rows:
       print(row)
       
    collCursor.close()
    conn.close()
    
    return rows, columns