import mysql.connector
import cx_Oracle
from typing import List, Tuple

def transfer_data_in_chunks(
    mysql_config: dict,
    oracle_config: dict,
    source_table: str,
    target_table: str,
    chunk_size: int = 1000
):
    """
    Transfer data from MySQL to Oracle in chunks.
    
    Args:
        mysql_config: MySQL connection config (host, user, password, database)
        oracle_config: Oracle connection config (user, password, dsn)
        source_table: Source table name in MySQL
        target_table: Target table name in Oracle
        chunk_size: Number of rows per chunk (default: 1000)
    """
    
    mysql_conn = None
    oracle_conn = None
    
    try:
        # Connect to MySQL
        mysql_conn = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_conn.cursor(buffered=True)
        
        # Connect to Oracle
        oracle_conn = oracle_config
        oracle_cursor = oracle_conn.cursor()
        
        # Get column names from MySQL table
        mysql_cursor.execute(f"SELECT * FROM sp_metricplot LIMIT 0")
        columns = [desc[0] for desc in mysql_cursor.description]
        print(f"Columns defined: {columns} ...")
        column_count = len(columns)
        
        # Prepare Oracle insert statement
        placeholders = ', '.join([f':{i+1}' for i in range(column_count)])
        print(f"Placeholders defined: {placeholders} ...")
        insert_sql = f"INSERT INTO sp_metricplot VALUES ({placeholders})"
        
        # Read and transfer data in chunks
        mysql_cursor.execute(f"SELECT * FROM SP_METRICPLOT")
        
        total_rows = 0
        chunk = []
        
        for row in mysql_cursor:
            chunk.append(row)
            
            if len(chunk) >= chunk_size:
                # Insert chunk into Oracle
                oracle_cursor.executemany(insert_sql, chunk)
                oracle_conn.commit()
                
                total_rows += len(chunk)
                print(f"Transferred {total_rows} rows...")
                
                chunk = []
        
        # Insert remaining rows
        if chunk:
            oracle_cursor.executemany(insert_sql, chunk)
            oracle_conn.commit()
            total_rows += len(chunk)
        
        print(f"Transfer complete! Total rows transferred: {total_rows}")
        
    except mysql.connector.Error as e:
        print(f"MySQL Error: {e}")
        raise
    except cx_Oracle.Error as e:
        print(f"Oracle Error: {e}")
        raise
    finally:
        # Clean up connections
        if mysql_conn:
            mysql_conn.close()
        if oracle_conn:
            oracle_conn.close()


# Example usage
if __name__ == "__main__":
    # MySQL configuration
    mysql_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'welcome1',
        'database': 'pyespdb'
    }

    cx_Oracle.init_oracle_client(
       lib_dir="/Users/henry.d.tullis/development/oracle/InstantClient/instantclient_23_3",
       config_dir="/Users/henry.d.tullis/.oci/Wallet_pyespdb/Wallet_pespdb.zip"
    )

    oracle_config = cx_Oracle.connect(
        user="pyesp",  # or your username
        password="Welcome_1961",
        dsn="pespdb_high",  # From tnsnames.ora (e.g., mydb_high, mydb_medium)
    )
 
    transfer_data_in_chunks(
        mysql_config=mysql_config,
        oracle_config=oracle_config,
        source_table='source_table_name',
        target_table='target_table_name',
        chunk_size=1000
    )
