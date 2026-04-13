"""
Configuration module for ESP (Enhanced Sizing and Provisioning) processor
"""
import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    """Configuration settings for ESP processor"""

    # Database Configuration — defaults match pyespdb PostgreSQL setup
    DB_USER: str = field(default_factory=lambda: os.getenv('ESP_DB_USER', 'htullis'))
    DB_PASSWORD: str = field(default_factory=lambda: os.getenv('ESP_DB_PASSWORD', ''))
    DB_HOST: str = field(default_factory=lambda: os.getenv('ESP_DB_HOST', 'localhost'))
    DB_NAME: str = field(default_factory=lambda: os.getenv('ESP_DB_NAME', 'pyespdb'))
    DB_PORT: int = field(default_factory=lambda: int(os.getenv('ESP_DB_PORT', '5432')))
    DB_POOL_SIZE: int = 5

    # File Processing Configuration
    TEMP_DIR: str = "/tmp/espTempDir"
    FILE_PATTERN: str = "escp*.zip"
    CPU_FILE_PATTERN: str = "cpuinfo*.txt"
    ESCP_FILE_PATTERN: str = "escp*.csv"

    # Processing Configuration
    BATCH_SIZE: int = 1000
    MAX_WORKERS: int = 4

    # File Encoding
    DEFAULT_ENCODING: str = 'utf-8'
    FALLBACK_ENCODINGS: List[str] = field(default_factory=lambda: [
        'utf-8',
        'latin-1',
        'cp1252',
        'iso-8859-1',
    ])

    # Date Formats (in priority order)
    DATE_FORMATS: List[str] = field(default_factory=lambda: [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%m/%d/%Y %H:%M:%S',
        '%m/%d/%Y',
        '%d/%m/%Y',
    ])

    # Logging Configuration
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    LOG_FILE: str = 'esp_processor.log'
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Application Metadata
    APP_VERSION: str = '2.10'
    APP_VERSION_DATE: str = 'March 2026'
    APP_STATE: str = 'Production'
    APP_DESC: str = 'Enhanced Sizing and Provisioning'

    def __post_init__(self):
        os.makedirs(self.TEMP_DIR, exist_ok=True)

    @property
    def db_config(self) -> dict:
        """Return psycopg2-compatible connection keyword arguments."""
        return {
            'user': self.DB_USER,
            'password': self.DB_PASSWORD,
            'host': self.DB_HOST,
            'dbname': self.DB_NAME,
            'port': self.DB_PORT,
        }


# Global configuration instance
CONFIG = Config()
