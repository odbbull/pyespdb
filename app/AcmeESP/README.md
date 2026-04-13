# ESP Processor - Enhanced Sizing and Provisioning

Refactored version 2.00 with improved error handling, logging, and maintainability.

## Overview

The ESP Processor handles collection files from Oracle database environments, extracting performance metrics and system information for storage and analysis.

## Architecture

### Module Structure

```
esp_refactored/
├── config.py              # Configuration management
├── database.py            # Database operations and connection pooling
├── file_processor.py      # File parsing and extraction
├── orchestrator.py        # Main workflow coordination
├── esp_processor.py       # CLI entry point
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Key Components

1. **Configuration (`config.py`)**
   - Centralized configuration using dataclasses
   - Environment variable support
   - Default values with override capability

2. **Database Layer (`database.py`)**
   - Connection pooling for efficiency
   - Context managers for safe resource handling
   - Batch insert operations
   - Comprehensive error handling

3. **File Processing (`file_processor.py`)**
   - Multi-encoding support
   - Robust CSV parsing with error recovery
   - Multiple date format handling
   - Batch processing for large files

4. **Orchestration (`orchestrator.py`)**
   - High-level workflow coordination
   - Statistics tracking
   - Error aggregation and reporting

5. **CLI Interface (`esp_processor.py`)**
   - Argument parsing
   - Logging configuration
   - Environment validation

## Features

### Improvements Over Original

- ✅ **Error Handling**: Try-except blocks around all critical operations
- ✅ **Resource Management**: Context managers for files and database connections
- ✅ **Batch Processing**: Configurable batch sizes for database inserts
- ✅ **Multi-Encoding Support**: Handles various file encodings automatically
- ✅ **Comprehensive Logging**: Structured logging with file and console output
- ✅ **Configuration Externalization**: Environment variables and config file
- ✅ **Connection Pooling**: Efficient database connection reuse
- ✅ **Date Format Flexibility**: Multiple date formats supported
- ✅ **Statistics Tracking**: Detailed processing metrics
- ✅ **Modular Design**: Separated concerns for maintainability
- ✅ **Type Hints**: Better code documentation and IDE support

## Installation

### Prerequisites

- Python 3.8 or higher
- MySQL/MariaDB database
- Access to ESP collection files

### Setup

```bash
# Clone or copy the refactored code
cd esp_refactored

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Set environment variables for database credentials:

```bash
export ACME_DB_USER="acme"
export ACME_DB_PASSWORD="your_password"
export ACME_DB_HOST="127.0.0.1"
export ACME_DB_NAME="AcmeAnvil"
export ACME_DB_PORT="3306"
export LOG_LEVEL="INFO"  # Optional: DEBUG, INFO, WARNING, ERROR
```

Or create a `.env` file and use a tool like `python-dotenv` to load it.

## Usage

### Basic Usage

```bash
# Process a collection
python esp_processor.py -c 12345

# Process with verbose output
python esp_processor.py -c 12345 -v

# Dry run (validate without processing)
python esp_processor.py -c 12345 --dry-run

# Custom log file
python esp_processor.py -c 12345 --log-file /var/log/esp.log
```

### Command Line Options

```
-c, --collection ID    Collection ID to process (required)
-v, --verbose          Enable verbose (DEBUG) logging
--version              Show version information
--dry-run              Validate configuration without processing
--log-file PATH        Specify log file path
```

## Configuration Options

Edit `config.py` or use environment variables:

### Database Settings
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_NAME`: Database name
- `DB_PORT`: Database port
- `DB_POOL_SIZE`: Connection pool size (default: 5)

### Processing Settings
- `TEMP_DIR`: Temporary extraction directory
- `BATCH_SIZE`: Batch insert size (default: 1000)
- `MAX_WORKERS`: Parallel processing workers

### File Patterns
- `FILE_PATTERN`: ZIP file pattern (escp*.zip)
- `CPU_FILE_PATTERN`: CPU info pattern (cpuinfo*.txt)
- `ESCP_FILE_PATTERN`: CSV file pattern (escp*.csv)

### Logging
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `LOG_FILE`: Log file path
- `LOG_FORMAT`: Log message format

## Database Schema

The processor expects these tables:

### sp_collection
```sql
- coll_id
- coll_dir_location
- sp_project_pr_id
```

### sp_project
```sql
- pr_id
- sp_client_cl_id
```

### sp_client
```sql
- cl_id
- cl_name
```

### sp_database
```sql
- db_id (AUTO_INCREMENT)
- db_name
- db_shortname
- db_filename
- db_collection_host
- db_host_cpu
- db_host_model
- sp_collection_coll_id
```

### sp_DbIdentity
```sql
- iden_id (AUTO_INCREMENT)
- iden_metric
- iden_acronym
- iden_instance
- iden_metricdate
- iden_metricvalue
- sp_database_db_id
```

### sp_DbMetric
```sql
- metr_id (AUTO_INCREMENT)
- metr_metric
- metr_acronym
- metr_instance
- metr_metricdate
- metr_metricvalue
- sp_database_db_id
```

## File Format

### ESCP CSV Format
```csv
METGROUP,METRIC,INSTANCE,DATE,VALUE
HOSTNAME,ServerName,,2024-12-13T10:30:00,server01
VERSION,DBVersion,,2024-12-13T10:30:00,19.21.0.0
CPU,CPUCount,1,2024-12-13T10:30:00,16
...
```

### CPU Info Format
```
CPU Type: Intel(R) Xeon(R) CPU E5-2690 v4
Dell PowerEdge R630
```

## Logging

Logs are written to both console and file:

- **Console**: INFO level and above (ERROR, WARNING, INFO)
- **File**: All levels including DEBUG
- **Format**: `timestamp - module - level - message`

Example log output:
```
2024-12-13 10:30:00 - orchestrator - INFO - Starting collection processing: 12345
2024-12-13 10:30:01 - database - INFO - Database connection pool initialized
2024-12-13 10:30:02 - file_processor - INFO - Extracting 3 files from escp_host01_db01.zip
2024-12-13 10:30:05 - database - DEBUG - Inserted 1000 metric records
```

## Error Handling

The processor handles errors gracefully:

1. **File Errors**: Invalid zip files, missing files, encoding issues
2. **Database Errors**: Connection failures, constraint violations
3. **Parsing Errors**: Malformed CSV rows, invalid dates
4. **Resource Errors**: Disk space, permissions

All errors are:
- Logged with full context
- Tracked in statistics
- Reported in final summary
- Won't stop processing of other files

## Performance Considerations

### Batch Processing
- Default batch size: 1000 records
- Adjustable via `CONFIG.BATCH_SIZE`
- Reduces database round trips

### Connection Pooling
- Reuses database connections
- Configurable pool size
- Automatic connection management

### Memory Efficiency
- Streams large files
- Processes in batches
- Clears temp directory after each file

## Testing

### Manual Testing
```bash
# Test with verbose output
python esp_processor.py -c TEST123 -v

# Dry run to validate configuration
python esp_processor.py -c TEST123 --dry-run
```

### Unit Testing (Future)
```bash
# Run unit tests (when implemented)
python -m pytest tests/

# Run with coverage
python -m pytest --cov=. tests/
```

## Migration from Original

To migrate from `aaBase.py`:

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables for database credentials
3. Test with dry-run mode: `--dry-run`
4. Process a small test collection first
5. Compare results with original implementation
6. Migrate to refactored version

Key differences:
- Configuration now in `config.py` instead of hardcoded
- Better error messages and logging
- Statistics and progress tracking
- Safer resource handling
- Batch processing for better performance

## Troubleshooting

### Database Connection Issues
```bash
# Check environment variables
echo $ACME_DB_USER
echo $ACME_DB_HOST

# Test database connection
mysql -u $ACME_DB_USER -p -h $ACME_DB_HOST $ACME_DB_NAME
```

### File Processing Issues
```bash
# Check file permissions
ls -la /path/to/collection/

# Verify zip files
unzip -t escp_file.zip

# Check temp directory
ls -la /tmp/espTempDir/
```

### Encoding Issues
- The processor tries multiple encodings automatically
- Check logs for encoding warnings
- Add custom encodings to `CONFIG.FALLBACK_ENCODINGS`

## Future Enhancements

Potential improvements:

- [ ] Parallel processing of multiple files
- [ ] Progress bars for long operations
- [ ] Email notifications on completion
- [ ] REST API for remote triggering
- [ ] Dashboard integration (Dash/Plotly)
- [ ] Data validation rules engine
- [ ] Automatic retry on transient failures
- [ ] Archive old processed files
- [ ] Integration with Oracle Cloud Infrastructure
- [ ] Real-time monitoring metrics

## Support

For issues or questions:
1. Check logs in `esp_processor.log`
2. Run with `-v` flag for detailed output
3. Use `--dry-run` to validate configuration
4. Review error messages in final statistics

## License

Internal use - Acme Corporation

## Version History

- **2.00** (December 2024) - Complete refactoring with improved architecture
- **1.00** (October 2022) - Original implementation
