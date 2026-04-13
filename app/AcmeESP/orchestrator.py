"""
Main orchestration module for ESP processing
"""
import os
import logging
from typing import List, Dict
from dataclasses import dataclass
from config import CONFIG
from database import DatabaseConnection, DatabaseOperations, DatabaseError
from file_processor import (
    FileProcessor, 
    CPUDetailsParser, 
    ESCPParser,
    FileProcessingError
)

logger = logging.getLogger(__name__)


@dataclass
class ProcessingStats:
    """Statistics for processing operations"""
    total_files: int = 0
    successful_files: int = 0
    failed_files: int = 0
    total_identity_records: int = 0
    total_metric_records: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    def add_error(self, error: str):
        """Add an error to the list"""
        self.errors.append(error)
    
    def __str__(self):
        return (
            f"Processing Summary:\n"
            f"  Files Processed: {self.successful_files}/{self.total_files}\n"
            f"  Failed: {self.failed_files}\n"
            f"  Identity Records: {self.total_identity_records}\n"
            f"  Metric Records: {self.total_metric_records}\n"
            f"  Errors: {len(self.errors)}"
        )


class ESPOrchestrator:
    """Orchestrates the entire ESP processing workflow"""
    
    def __init__(self):
        self.db_connection = DatabaseConnection()
        self.db_ops = DatabaseOperations(self.db_connection)
        self.file_processor = FileProcessor()
        self.stats = ProcessingStats()
    
    def get_collection_directories(self, collection_dir: str) -> List[str]:
        """
        Get all subdirectories in the collection directory
        
        Args:
            collection_dir: Root collection directory
            
        Returns:
            List of subdirectory names
        """
        try:
            if not os.path.exists(collection_dir):
                raise FileProcessingError(f"Collection directory not found: {collection_dir}")
            
            dir_list = [
                d for d in os.listdir(collection_dir)
                if os.path.isdir(os.path.join(collection_dir, d))
            ]
            
            logger.info(f"Found {len(dir_list)} directories in {collection_dir}")
            return dir_list
            
        except Exception as e:
            logger.error(f"Error reading collection directory: {e}")
            raise
    
    def get_database_files(self, host_dir: str) -> List[str]:
        """
        Get all database zip files in a host directory
        
        Args:
            host_dir: Host directory path
            
        Returns:
            List of database file paths
        """
        pattern = os.path.join(host_dir, CONFIG.FILE_PATTERN)
        import glob
        files = glob.glob(pattern)
        
        logger.debug(f"Found {len(files)} database files in {host_dir}")
        return files
    
    def process_host_file(
        self,
        collection_id: str,
        host_file: str
    ) -> bool:
        """
        Process a single host file
        
        Args:
            collection_id: Collection ID
            host_file: Path to host zip file
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Processing host file: {host_file}")
        
        try:
            # Insert database record
            database_id = self.db_ops.insert_database_record(
                collection_id,
                os.path.basename(host_file)
            )
            
            # Extract zip file
            extracted_files = self.file_processor.extract_zip_file(host_file)
            logger.debug(f"Extracted {len(extracted_files)} files")
            
            # Find CPU info file
            cpu_files = self.file_processor.find_files_by_pattern(
                CONFIG.TEMP_DIR,
                CONFIG.CPU_FILE_PATTERN
            )
            
            # Process CPU details if available
            if cpu_files:
                cpu_type, server_model = CPUDetailsParser.parse_cpu_file(cpu_files[0])
                if cpu_type or server_model:
                    self.db_ops.update_cpu_details(database_id, cpu_type, server_model)
            else:
                logger.warning("No CPU info file found")
            
            # Find ESCP file
            escp_files = self.file_processor.find_files_by_pattern(
                CONFIG.TEMP_DIR,
                CONFIG.ESCP_FILE_PATTERN
            )
            
            if not escp_files:
                raise FileProcessingError("No ESCP file found in archive")
            
            # Process ESCP file
            identity_batch, metric_batch, parse_stats = ESCPParser.parse_escp_file(
                escp_files[0],
                database_id
            )
            
            # Insert batches
            if identity_batch:
                # Process in batches
                for i in range(0, len(identity_batch), CONFIG.BATCH_SIZE):
                    batch = identity_batch[i:i + CONFIG.BATCH_SIZE]
                    self.db_ops.insert_identity_batch(batch)
                    logger.debug(f"Inserted identity batch {i // CONFIG.BATCH_SIZE + 1}")
            
            if metric_batch:
                # Process in batches
                for i in range(0, len(metric_batch), CONFIG.BATCH_SIZE):
                    batch = metric_batch[i:i + CONFIG.BATCH_SIZE]
                    self.db_ops.insert_metric_batch(batch)
                    logger.debug(f"Inserted metric batch {i // CONFIG.BATCH_SIZE + 1}")
            
            # Update statistics
            self.stats.total_identity_records += parse_stats['identity_records']
            self.stats.total_metric_records += parse_stats['metric_records']
            
            # Clear temp directory
            self.file_processor.clear_temp_directory()
            
            # Rename processed file
            self._rename_processed_file(host_file)
            
            self.stats.successful_files += 1
            logger.info(f"Successfully processed {host_file}")
            return True
            
        except Exception as e:
            error_msg = f"Error processing {host_file}: {e}"
            logger.error(error_msg, exc_info=True)
            self.stats.add_error(error_msg)
            self.stats.failed_files += 1
            
            # Clean up temp directory even on failure
            try:
                self.file_processor.clear_temp_directory()
            except Exception as cleanup_error:
                logger.error(f"Error during cleanup: {cleanup_error}")
            
            return False
    
    def _rename_processed_file(self, file_path: str) -> None:
        """
        Rename processed file with 'O' suffix
        
        Args:
            file_path: Original file path
        """
        try:
            new_path = file_path + 'O'
            os.rename(file_path, new_path)
            logger.debug(f"Renamed {file_path} to {new_path}")
        except Exception as e:
            logger.warning(f"Could not rename processed file: {e}")
    
    def process_directory(
        self,
        collection_id: str,
        collection_dir: str,
        subdir_name: str
    ) -> None:
        """
        Process all files in a subdirectory
        
        Args:
            collection_id: Collection ID
            collection_dir: Root collection directory
            subdir_name: Subdirectory name
        """
        host_dir = os.path.join(collection_dir, subdir_name)
        logger.info(f"Processing directory: {host_dir}")
        
        try:
            database_files = self.get_database_files(host_dir)
            
            if not database_files:
                logger.warning(f"No database files found in {host_dir}")
                return
            
            for host_file in database_files:
                self.stats.total_files += 1
                self.process_host_file(collection_id, host_file)
                
        except Exception as e:
            error_msg = f"Error processing directory {host_dir}: {e}"
            logger.error(error_msg, exc_info=True)
            self.stats.add_error(error_msg)
    
    def process_collection(self, collection_id: str) -> ProcessingStats:
        """
        Process an entire collection
        
        Args:
            collection_id: Collection ID to process
            
        Returns:
            ProcessingStats object with results
        """
        logger.info(f"Starting collection processing: {collection_id}")
        
        try:
            # Get collection information
            coll_dir, client_id, client_name = self.db_ops.get_client_collection(
                collection_id
            )
            logger.info(f"Processing collection for client: {client_name} ({client_id})")
            
            # Get all subdirectories
            subdirs = self.get_collection_directories(coll_dir)
            
            if not subdirs:
                logger.warning(f"No subdirectories found in {coll_dir}")
                return self.stats
            
            # Process each subdirectory
            for subdir in subdirs:
                self.process_directory(collection_id, coll_dir, subdir)
            
            logger.info(f"Collection processing complete")
            logger.info(str(self.stats))
            
        except DatabaseError as e:
            logger.error(f"Database error during collection processing: {e}")
            self.stats.add_error(str(e))
        except FileProcessingError as e:
            logger.error(f"File processing error: {e}")
            self.stats.add_error(str(e))
        except Exception as e:
            logger.error(f"Unexpected error during collection processing: {e}", exc_info=True)
            self.stats.add_error(str(e))
        
        return self.stats
