# Migration Guide: aaBase.py → ESP Processor v2.0

## Overview

This guide helps you migrate from the original `aaBase.py` implementation to the refactored ESP Processor v2.0.

## Key Differences

### Architecture

| Aspect | Original (v1.0) | Refactored (v2.0) |
|--------|----------------|-------------------|
| Structure | Single file | Modular (5 files) |
| Configuration | Hardcoded | Externalized (env vars) |
| Error Handling | Minimal | Comprehensive |
| Logging | Print statements | Structured logging |
| Database | Direct connection | Connection pooling |
| Resource Management | Manual | Context managers |
| Testing | None | Unit test structure |

### File Structure Comparison

**Original:**
```
aaBase.py (everything in one file)
```

**Refactored:**
```
esp_refactored/
├── config.py              # Configuration
├── database.py            # DB operations
├── file_processor.py      # File parsing
├── orchestrator.py        # Workflow
├── esp_processor.py       # CLI entry
├── requirements.txt       # Dependencies
├── README.md             # Documentation
└── tests/                # Unit tests
```

## Function Mapping

### Original → Refactored

| Original Function | Refactored Location | Notes |
|-------------------|---------------------|-------|
| `getDBConnection()` | `database.DatabaseConnection()` | Now uses connection pooling |
| `getClientCollection()` | `database.DatabaseOperations.get_client_collection()` | Better error handling |
| `insSpDatabase()` | `database.DatabaseOperations.insert_database_record()` | Improved validation |
| `loadCpuDetails()` | `database.DatabaseOperations.update_cpu_details()` | Transaction support |
| `unzHostFile()` | `file_processor.FileProcessor.extract_zip_file()` | Validation added |
| `clearTempDir()` | `file_processor.FileProcessor.clear_temp_directory()` | Error handling |
| `readCpuDetails()` | `file_processor.CPUDetailsParser.parse_cpu_file()` | Multi-encoding support |
| `procEscpDetails()` | `file_processor.ESCPParser.parse_escp_file()` | Batch processing |
| Main program | `esp_processor.main()` | Argument parsing, logging |

## Migration Steps

### 1. Backup Current System

```bash
# Backup original script
cp aaBase.py aaBase.py.backup

# Backup database (if applicable)
mysqldump -u acme -p AcmeAnvil > backup_$(date +%Y%m%d).sql
```

### 2. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd esp_refactored
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.template .env

# Edit with your credentials
nano .env

# Or export directly
export ACME_DB_USER="acme"
export ACME_DB_PASSWORD="your_password"
export ACME_DB_HOST="127.0.0.1"
export ACME_DB_NAME="AcmeAnvil"
```

### 4. Test Configuration

```bash
# Dry run to validate
python esp_processor.py -c TEST_COLLECTION --dry-run

# Should output:
# DRY RUN MODE - No files will be processed
# Collection ID: TEST_COLLECTION
# Configuration validated successfully
```

### 5. Parallel Testing

Run both versions on the same test collection:

```bash
# Original version
python aaBase.py -c TEST123

# New version (verbose)
python esp_processor.py -c TEST123 -v

# Compare results in database
```

### 6. Validation Queries

```sql
-- Compare record counts
SELECT 
    db_name,
    (SELECT COUNT(*) FROM sp_DbIdentity WHERE sp_database_db_id = d.db_id) as identity_count,
    (SELECT COUNT(*) FROM sp_DbMetric WHERE sp_database_db_id = d.db_id) as metric_count
FROM sp_database d
WHERE sp_collection_coll_id = 'TEST123'
ORDER BY db_name;

-- Check for differences in values
SELECT * FROM sp_DbMetric 
WHERE sp_database_db_id IN (
    SELECT db_id FROM sp_database WHERE sp_collection_coll_id = 'TEST123'
)
LIMIT 100;
```

## Code Changes Required

### Database Credentials

**Original:**
```python
acmeConn = mysql.connector.connect(
    user='acme', 
    password='welcome1',
    host='127.0.0.1', 
    database='AcmeAnvil'
)
```

**Refactored:**
```python
# Set in environment
export ACME_DB_PASSWORD="your_password"

# Code automatically uses CONFIG
db_connection = DatabaseConnection()
```

### Error Handling

**Original:**
```python
# No try-except, errors crash program
cursor.execute(query, params)
```

**Refactored:**
```python
# Comprehensive error handling
try:
    cursor.execute(query, params)
    conn.commit()
except Error as err:
    conn.rollback()
    logger.error(f"Query failed: {err}")
    raise DatabaseError(f"Operation failed: {err}")
```

### File Processing

**Original:**
```python
# Simple open, crashes on encoding issues
with open(pFileName[0]) as espCsvFile:
    csv_reader = csv.reader(espCsvFile, delimiter=',')
```

**Refactored:**
```python
# Multi-encoding support
for encoding in CONFIG.FALLBACK_ENCODINGS:
    try:
        with open(file_path, 'r', encoding=encoding) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            # ... process file
            break
    except UnicodeDecodeError:
        continue
```

### Batch Processing

**Original:**
```python
# Individual inserts
for csvRow in csv_reader:
    vCursor.execute(vQuery, (data,))
```

**Refactored:**
```python
# Batch inserts
batch = []
for csvRow in csv_reader:
    batch.append((data,))
    
    if len(batch) >= CONFIG.BATCH_SIZE:
        cursor.executemany(query, batch)
        batch = []

# Insert remaining
if batch:
    cursor.executemany(query, batch)
```

## Command Line Differences

### Original Usage

```bash
python aaBase.py -c 12345
```

### Refactored Usage

```bash
# Basic usage (same)
python esp_processor.py -c 12345

# With verbose logging (new)
python esp_processor.py -c 12345 -v

# Dry run validation (new)
python esp_processor.py -c 12345 --dry-run

# Custom log file (new)
python esp_processor.py -c 12345 --log-file /var/log/esp.log
```

## Output Differences

### Original Output
```
File:  ['/tmp/espTempDir/escp_file.csv']  processed  1500  lines
```

### Refactored Output
```
2024-12-13 10:30:00 - orchestrator - INFO - Processing host file: escp_file.zip
2024-12-13 10:30:01 - database - INFO - Inserted database record: db01 (ID: 123)
2024-12-13 10:30:02 - file_processor - INFO - Parsed escp_file.csv: 1200 identity, 300 metric records
2024-12-13 10:30:03 - orchestrator - INFO - Successfully processed escp_file.zip

Processing Summary:
  Files Processed: 1/1
  Failed: 0
  Identity Records: 1200
  Metric Records: 300
  Errors: 0
```

## Performance Considerations

### Memory Usage

**Original:**
- Loads entire file into memory
- Individual database inserts

**Refactored:**
- Streams large files
- Batch inserts (1000 records at a time)
- Connection pooling reduces overhead

### Expected Performance Improvements

- **Database Operations:** 5-10x faster (batch inserts)
- **Connection Overhead:** Reduced (connection pooling)
- **Large Files:** More stable (streaming)

## Troubleshooting Migration Issues

### Issue: Import Errors

```bash
# Error: ModuleNotFoundError: No module named 'mysql'
# Solution:
pip install mysql-connector-python
```

### Issue: Database Connection Fails

```bash
# Error: DatabaseError: Invalid username or password
# Solution: Check environment variables
echo $ACME_DB_USER
echo $ACME_DB_PASSWORD

# Or check .env file
cat .env
```

### Issue: Different Record Counts

```sql
-- Debug: Check what's being inserted
SELECT * FROM sp_DbMetric 
WHERE sp_database_db_id = 123
ORDER BY metr_id DESC
LIMIT 10;
```

### Issue: Encoding Errors

```bash
# Original might skip some files silently
# Refactored logs encoding attempts:
# Check logs for: "Failed to decode with utf-8, trying next encoding"
```

## Rollback Plan

If you need to rollback:

```bash
# 1. Stop using new version
# 2. Restore original script
cp aaBase.py.backup aaBase.py

# 3. If needed, restore database
mysql -u acme -p AcmeAnvil < backup_YYYYMMDD.sql

# 4. Continue with original version
python aaBase.py -c COLLECTION_ID
```

## Validation Checklist

Before full migration:

- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] Database connection tested
- [ ] Dry run successful
- [ ] Test collection processed successfully
- [ ] Record counts match original
- [ ] Sample data validation passed
- [ ] Performance acceptable
- [ ] Logs reviewed
- [ ] Error handling tested

## Long-term Benefits

After migration, you gain:

1. **Maintainability**: Modular code easier to update
2. **Reliability**: Better error handling and recovery
3. **Visibility**: Comprehensive logging and statistics
4. **Performance**: Batch processing and connection pooling
5. **Testability**: Unit test structure in place
6. **Extensibility**: Easy to add new features
7. **Security**: Credentials in environment, not code

## Next Steps

After successful migration:

1. Archive original `aaBase.py`
2. Update deployment documentation
3. Train team on new CLI options
4. Set up log rotation
5. Configure monitoring/alerting
6. Implement automated testing
7. Plan future enhancements (see README)

## Support

For migration assistance:
1. Review logs: `esp_processor.log`
2. Use verbose mode: `-v`
3. Compare database results
4. Check configuration: `--dry-run`
