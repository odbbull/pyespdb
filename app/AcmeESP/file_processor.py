"""
File processing module for ESP files
"""
import os
import csv
import logging
import zipfile
from datetime import datetime
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass
from config import CONFIG

logger = logging.getLogger(__name__)


@dataclass
class ParsedRow:
    """Represents a parsed CSV row"""
    group_name: str
    metric_name: str
    instance_no: str
    metric_date: datetime
    metric_value: str
    is_identity: bool


class FileProcessingError(Exception):
    """Custom exception for file processing errors"""
    pass


class FileProcessor:
    """Handles file operations for ESP processing"""
    
    @staticmethod
    def validate_zip_file(file_path: str) -> bool:
        """
        Validate if file exists and is a valid zip file
        
        Args:
            file_path: Path to zip file
            
        Returns:
            True if valid, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        
        if not zipfile.is_zipfile(file_path):
            logger.error(f"Invalid zip file: {file_path}")
            return False
        
        return True
    
    @staticmethod
    def extract_zip_file(zip_path: str, extract_to: str = CONFIG.TEMP_DIR) -> List[str]:
        """
        Extract zip file to temporary directory
        
        Args:
            zip_path: Path to zip file
            extract_to: Destination directory
            
        Returns:
            List of extracted file paths
        """
        if not FileProcessor.validate_zip_file(zip_path):
            raise FileProcessingError(f"Invalid zip file: {zip_path}")
        
        os.makedirs(extract_to, exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get list of files in zip
                file_list = zip_ref.namelist()
                logger.info(f"Extracting {len(file_list)} files from {zip_path}")
                
                # Extract all files
                zip_ref.extractall(extract_to)
                
                # Return full paths of extracted files
                extracted_files = [
                    os.path.join(extract_to, filename) 
                    for filename in file_list
                ]
                
                logger.info(f"Successfully extracted to {extract_to}")
                return extracted_files
                
        except zipfile.BadZipFile as e:
            raise FileProcessingError(f"Corrupted zip file {zip_path}: {e}")
        except Exception as e:
            raise FileProcessingError(f"Failed to extract {zip_path}: {e}")
    
    @staticmethod
    def clear_temp_directory(temp_dir: str = CONFIG.TEMP_DIR) -> int:
        """
        Clear all files from temporary directory
        
        Args:
            temp_dir: Directory to clear
            
        Returns:
            Number of files removed
        """
        if not os.path.exists(temp_dir):
            return 0
        
        file_count = 0
        try:
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    file_count += 1
            
            logger.debug(f"Cleared {file_count} files from {temp_dir}")
            return file_count
            
        except Exception as e:
            logger.error(f"Error clearing temp directory: {e}")
            raise FileProcessingError(f"Failed to clear temp directory: {e}")
    
    @staticmethod
    def find_files_by_pattern(directory: str, pattern: str) -> List[str]:
        """
        Find files matching a pattern in a directory
        
        Args:
            directory: Directory to search
            pattern: File pattern (e.g., 'escp*.csv')
            
        Returns:
            List of matching file paths
        """
        import glob
        
        search_path = os.path.join(directory, pattern)
        files = glob.glob(search_path)
        
        logger.debug(f"Found {len(files)} files matching pattern '{pattern}'")
        return files


class CPUDetailsParser:
    """Parser for CPU details files"""
    
    @staticmethod
    def parse_cpu_file(file_path: str) -> Tuple[str, str]:
        """
        Parse CPU details from file
        
        Args:
            file_path: Path to CPU info file
            
        Returns:
            Tuple of (cpu_type, server_model)
        """
        cpu_type = ''
        server_model = ''
        
        if not os.path.exists(file_path):
            logger.warning(f"CPU file not found: {file_path}")
            return cpu_type, server_model
        
        try:
            # Try multiple encodings
            for encoding in CONFIG.FALLBACK_ENCODINGS:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                logger.error(f"Could not decode CPU file with any encoding: {file_path}")
                return cpu_type, server_model
            
            if len(lines) < 2:
                logger.warning(f"CPU file has insufficient lines: {file_path}")
                return cpu_type, server_model
            
            # Parse first line for CPU type
            first_line = lines[0].strip()
            if ':' in first_line:
                parts = first_line.split(':', 1)
                cpu_type = parts[1].strip()
            
            # Parse second line for server model
            if len(lines) > 1:
                server_model = lines[1].strip()
            
            logger.info(f"Parsed CPU details: {cpu_type}, {server_model}")
            return cpu_type, server_model
            
        except Exception as e:
            logger.error(f"Error parsing CPU file {file_path}: {e}")
            return cpu_type, server_model


class ESCPParser:
    """Parser for ESCP CSV files"""
    
    @staticmethod
    def parse_date(date_string: str) -> datetime:
        """
        Parse date string with multiple format support
        
        Args:
            date_string: Date string to parse
            
        Returns:
            Parsed datetime object
        """
        if not date_string or date_string.strip() == '':
            return datetime.today()
        
        date_string = date_string.strip()
        
        # Try each date format
        for date_format in CONFIG.DATE_FORMATS:
            try:
                return datetime.strptime(date_string, date_format)
            except ValueError:
                continue
        
        # If no format matches, log warning and return today
        logger.warning(f"Could not parse date '{date_string}', using current date")
        return datetime.today()
    
    @staticmethod
    def parse_row(csv_row: List[str], is_identity: bool) -> Optional[ParsedRow]:
        """
        Parse a single CSV row
        
        Args:
            csv_row: List of CSV fields
            is_identity: Whether this is an identity row
            
        Returns:
            ParsedRow object or None if row should be skipped
        """
        # Validate row has minimum columns
        if len(csv_row) < 5:
            logger.debug(f"Row has insufficient columns ({len(csv_row)}), skipping")
            return None
        
        group_name = csv_row[0].strip()
        metric_name = csv_row[1].strip()
        instance_no = csv_row[2].strip() if csv_row[2].strip() else '1'
        date_string = csv_row[3].strip()
        metric_value = csv_row[4].strip()
        
        # Skip header rows
        if group_name == 'METGROUP':
            return None
        
        # Skip empty rows
        if not group_name or not metric_name:
            return None
        
        # Parse date
        metric_date = ESCPParser.parse_date(date_string)
        
        return ParsedRow(
            group_name=group_name,
            metric_name=metric_name,
            instance_no=instance_no,
            metric_date=metric_date,
            metric_value=metric_value,
            is_identity=is_identity
        )
    
    @staticmethod
    def parse_escp_file(
        file_path: str,
        database_id: int
    ) -> Tuple[List[Tuple], List[Tuple], Dict[str, int]]:
        """
        Parse ESCP CSV file and return batches for database insertion
        
        Args:
            file_path: Path to ESCP CSV file
            database_id: Database ID for foreign key
            
        Returns:
            Tuple of (identity_batch, metric_batch, statistics)
        """
        if not os.path.exists(file_path):
            raise FileProcessingError(f"ESCP file not found: {file_path}")
        
        identity_batch = []
        metric_batch = []
        
        stats = {
            'total_lines': 0,
            'identity_records': 0,
            'metric_records': 0,
            'skipped_lines': 0,
            'error_lines': 0
        }
        
        is_identity = True
        
        # Try multiple encodings
        for encoding in CONFIG.FALLBACK_ENCODINGS:
            try:
                with open(file_path, 'r', encoding=encoding, errors='replace') as csvfile:
                    csv_reader = csv.reader(csvfile, delimiter=',')
                    
                    for csv_row in csv_reader:
                        stats['total_lines'] += 1
                        
                        try:
                            parsed_row = ESCPParser.parse_row(csv_row, is_identity)
                            
                            if parsed_row is None:
                                stats['skipped_lines'] += 1
                                continue
                            
                            # Check if we transition from identity to metrics
                            if is_identity and parsed_row.group_name == 'CPU':
                                is_identity = False
                            
                            # Create tuple for database insertion
                            # (id omitted — GENERATED ALWAYS AS IDENTITY in PostgreSQL)
                            record = (
                                parsed_row.group_name,
                                parsed_row.metric_name,
                                parsed_row.instance_no,
                                parsed_row.metric_date,
                                parsed_row.metric_value,
                                database_id
                            )
                            
                            # Add to appropriate batch
                            if is_identity and parsed_row.group_name != 'CPU':
                                identity_batch.append(record)
                                stats['identity_records'] += 1
                            else:
                                metric_batch.append(record)
                                stats['metric_records'] += 1
                        
                        except Exception as e:
                            stats['error_lines'] += 1
                            logger.warning(
                                f"Error parsing line {stats['total_lines']}: {e}"
                            )
                            continue
                
                logger.info(
                    f"Parsed {file_path}: "
                    f"{stats['identity_records']} identity, "
                    f"{stats['metric_records']} metric records "
                    f"({stats['skipped_lines']} skipped, {stats['error_lines']} errors)"
                )
                
                return identity_batch, metric_batch, stats
                
            except UnicodeDecodeError:
                logger.debug(f"Failed to decode with {encoding}, trying next encoding")
                continue
        
        raise FileProcessingError(f"Could not decode {file_path} with any encoding")
