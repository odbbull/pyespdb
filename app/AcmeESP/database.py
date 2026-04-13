"""
Database connection and operations module for ESP processor (PostgreSQL)
"""
import logging
from contextlib import contextmanager
from typing import Optional, Tuple, List
import psycopg2
import psycopg2.pool
import psycopg2.extras
from config import CONFIG

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass


class DatabaseConnection:
    """Manages PostgreSQL connections with connection pooling"""

    def __init__(self):
        self._pool = None
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize psycopg2 connection pool"""
        try:
            self._pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=CONFIG.DB_POOL_SIZE,
                **CONFIG.db_config,
            )
            logger.info("Database connection pool initialized")
        except psycopg2.Error as err:
            logger.error(f"Failed to create connection pool: {err}")
            raise DatabaseError(f"Connection pool initialization failed: {err}")

    @contextmanager
    def get_connection(self):
        """Context manager for getting connections from pool"""
        conn = None
        try:
            conn = self._pool.getconn()
            logger.debug("Connection acquired from pool")
            yield conn
        except psycopg2.OperationalError as err:
            raise DatabaseError(f"Database connection failed: {err}")
        except psycopg2.Error as err:
            raise DatabaseError(f"Database error: {err}")
        finally:
            if conn is not None:
                self._pool.putconn(conn)
                logger.debug("Connection returned to pool")


class DatabaseOperations:
    """Database operations for ESP processing"""

    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection

    def get_client_collection(self, coll_id: str) -> Tuple[str, str, str]:
        """
        Get collection directory and client information.

        Returns:
            Tuple of (collection_dir, client_id, client_name)
        """
        query = """
            SELECT c.cl_id, c.cl_name, a.coll_dir_location
              FROM sp_collection a
              JOIN sp_project p ON a.sp_project_pr_id = p.pr_id
              JOIN sp_client  c ON p.sp_client_cl_id  = c.cl_id
             WHERE a.coll_id = %s
        """
        with self.db_connection.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, (coll_id,))
                result = cursor.fetchone()
                if not result:
                    raise DatabaseError(f"Collection {coll_id} not found")
                client_id, client_name, coll_dir = result
                logger.info(f"Retrieved collection info: {client_name} ({client_id})")
                return coll_dir, client_id, client_name
            finally:
                cursor.close()

    def insert_database_record(self, collection_id: str, host_file: str) -> int:
        """
        Insert a sp_database record and return the generated db_id.

        Filename convention: escp_<tag>_<host>_<dbname>.zip
        Parts after stripping the extension:  [0]=escp [1]=tag [2]=host [3]=dbname
        """
        # Strip extension then split so db_name is clean
        name_no_ext = host_file.rsplit('.', 1)[0]
        file_parts = name_no_ext.split("_")
        if len(file_parts) < 4:
            raise ValueError(
                f"Invalid host file format (expected escp_<tag>_<host>_<db>.zip): {host_file}"
            )

        host_name = file_parts[2]
        db_name = file_parts[3]
        db_shortname = db_name[:15]

        query = """
            INSERT INTO sp_database
              (db_name, db_shortname, db_filename, db_fileread_date,
               db_collection_host, is_cluster_fg, is_active_fg,
               sp_collection_coll_id)
            VALUES (%s, %s, %s, NOW(), %s, FALSE, TRUE, %s)
            RETURNING db_id
        """
        with self.db_connection.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    query,
                    (db_name, db_shortname, host_file, host_name, collection_id),
                )
                db_id = cursor.fetchone()[0]
                conn.commit()
                logger.info(f"Inserted database record: {db_name} (ID: {db_id})")
                return db_id
            except psycopg2.Error as err:
                conn.rollback()
                logger.error(f"Failed to insert database record: {err}")
                raise DatabaseError(f"Insert failed: {err}")
            finally:
                cursor.close()

    def update_cpu_details(
        self, database_id: int, cpu_type: str, server_model: str
    ) -> None:
        """Update CPU details for a database record"""
        query = """
            UPDATE sp_database
               SET db_host_cpu = %s, db_host_model = %s
             WHERE db_id = %s
        """
        with self.db_connection.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, (cpu_type, server_model, database_id))
                conn.commit()
                logger.info(f"Updated CPU details for database {database_id}")
            except psycopg2.Error as err:
                conn.rollback()
                logger.error(f"Failed to update CPU details: {err}")
                raise DatabaseError(f"Update failed: {err}")
            finally:
                cursor.close()

    def insert_identity_batch(self, batch_data: List[Tuple]) -> int:
        """
        Batch insert identity records into sp_dbidentity.

        Each tuple: (iden_metric, iden_acronym, iden_instance,
                     iden_metricdate, iden_metricvalue, sp_database_db_id)
        """
        query = """
            INSERT INTO sp_dbidentity
              (iden_metric, iden_acronym, iden_instance,
               iden_metricdate, iden_metricvalue, sp_database_db_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        with self.db_connection.get_connection() as conn:
            cursor = conn.cursor()
            try:
                psycopg2.extras.execute_batch(cursor, query, batch_data,
                                              page_size=CONFIG.BATCH_SIZE)
                conn.commit()
                row_count = cursor.rowcount
                logger.debug(f"Inserted {len(batch_data)} identity records")
                return len(batch_data)
            except psycopg2.Error as err:
                conn.rollback()
                logger.error(f"Failed to insert identity batch: {err}")
                raise DatabaseError(f"Batch insert failed: {err}")
            finally:
                cursor.close()

    def insert_metric_batch(self, batch_data: List[Tuple]) -> int:
        """
        Batch insert metric records into sp_dbmetric.

        Each tuple: (metr_metric, metr_acronym, metr_instance,
                     metr_metricdate, metr_metricvalue, sp_database_db_id)
        """
        query = """
            INSERT INTO sp_dbmetric
              (metr_metric, metr_acronym, metr_instance,
               metr_metricdate, metr_metricvalue, sp_database_db_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        with self.db_connection.get_connection() as conn:
            cursor = conn.cursor()
            try:
                psycopg2.extras.execute_batch(cursor, query, batch_data,
                                              page_size=CONFIG.BATCH_SIZE)
                conn.commit()
                logger.debug(f"Inserted {len(batch_data)} metric records")
                return len(batch_data)
            except psycopg2.Error as err:
                conn.rollback()
                logger.error(f"Failed to insert metric batch: {err}")
                raise DatabaseError(f"Batch insert failed: {err}")
            finally:
                cursor.close()
