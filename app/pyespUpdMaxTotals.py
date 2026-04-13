import oracledb
import pandas as pd
from pathlib import Path
import os
from contextlib import contextmanager

# ============================================
# Autonomous Database Connection Configuration
# ============================================
## For Autonomous Database, you need to set the wallet location
WALLET_LOCATION = "/Users/henry.d.tullis/.oci/Wallet_pyespdb/Wallet_pespdb"
WALLET_PASSWORD = "Welcome_1961"

## Set wallet location
os.environ["TNS_ADMIN"] = WALLET_LOCATION

def connect_autonomous_db():
    """Connect to Oracle Autonomous Database"""
    try:
       # Connection using service name from tnsnames.ora in wallet
       connection = oracledb.connect(
          user='pyesp',
          password='Welcome_1961',
          dsn='pespdb_high',
          config_dir=WALLET_LOCATION,
          wallet_location=WALLET_LOCATION,
          wallet_password=WALLET_PASSWORD
       )
    
       print("Successfully connected to Autonomous Database")
       return connection
    
    except oracledb.Error as error:
       print(f"Error connecting to Autonomous Database: {error}")
       return None
        
def getDatabaseList():

    conn = connect_autonomous_db()
    
    collCursor = conn.cursor()
    
    collCursor.execute("""
        select db_id,
               db_name,
               sp_collection_coll_id
          from sp_database
        order by 1;
            """)
    
    rows = collCursor.fetchall()
    
    columns = [col[0] for col in collCursor.description]
    
    print(f"Column names: {columns}")
    print(f"Total rows: {len(rows)}")
    
    for row in rows:
       print(row)
       
    collCursor.close()
    return conn, rows

def insDatabaseRecord(pConn, pRows):
    
##    vCursor = pConn.cursor()
    vSuccess = False
    print(f"Inside the insert database records")

    try:
        with pConn.cursor() as vCursor:
            insert_sql = """
               INSERT INTO sp_DbMaxTotals (
                   DMT_DBID,
                   DMT_DBNAME,
                   DMT_COLL_ID
                ) VALUES (:1, :2, :3)
            """

            inserted = 0
            skipped = 0
            errors = 0

            for row in pRows:
                try:
                    vCursor.execute(insert_sql, row)
                    print(f"this is the inserted row: {row}")
                    inserted += 1
                except oracledb.IntegrityError as e:
                    skipped += 1
                    print(f"--- skipped record due to integrity: {row}")
                except oracledb.IntegrityError as e:
                    errors += 1
                    print(f"--- skipped record due to other error: {row}")
            
        pConn.commit()
        
        print(f"++ Records successfully loaded to max totals")
        vSuccess = True

    except oracledb.Error as error:
        print(f"x Error during bulk insert: {error}")
        pConn.rollback()
        vSuccess = False

# ============================================
# Main Execution Examples
# ============================================

if __name__ == "__main__":
    
    # Example 1: Simple wallet connection
    print("Starting to get the database list")

    dbConn, dbRows = getDatabaseList()
    loadSuccess = False

    loadSuccess = insDatabaseRecord(dbConn,dbRows)

    print("End of the database collection")
    dbConn.close()