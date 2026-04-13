"""
Example unit tests for ESP Processor
Run with: python -m pytest tests/
"""
import unittest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG
from file_processor import ESCPParser, CPUDetailsParser, FileProcessor


class TestESCPParser(unittest.TestCase):
    """Test ESCP CSV parsing functionality"""
    
    def test_parse_date_standard_format(self):
        """Test parsing standard ISO format date"""
        date_string = "2024-12-13T10:30:00"
        result = ESCPParser.parse_date(date_string)
        
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 12)
        self.assertEqual(result.day, 13)
    
    def test_parse_date_alternative_format(self):
        """Test parsing alternative date format"""
        date_string = "2024-12-13 10:30:00"
        result = ESCPParser.parse_date(date_string)
        
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.year, 2024)
    
    def test_parse_date_invalid_returns_today(self):
        """Test that invalid date returns today's date"""
        date_string = "invalid-date"
        result = ESCPParser.parse_date(date_string)
        
        self.assertIsInstance(result, datetime)
        # Should be close to today (within 1 day)
        self.assertLess(abs((datetime.today() - result).days), 1)
    
    def test_parse_date_empty_returns_today(self):
        """Test that empty date returns today's date"""
        result = ESCPParser.parse_date("")
        
        self.assertIsInstance(result, datetime)
    
    def test_parse_row_valid_data(self):
        """Test parsing valid CSV row"""
        csv_row = ["HOSTNAME", "ServerName", "1", "2024-12-13T10:30:00", "server01"]
        result = ESCPParser.parse_row(csv_row, is_identity=True)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.group_name, "HOSTNAME")
        self.assertEqual(result.metric_name, "ServerName")
        self.assertEqual(result.instance_no, "1")
        self.assertEqual(result.metric_value, "server01")
    
    def test_parse_row_missing_instance_defaults_to_1(self):
        """Test that missing instance number defaults to '1'"""
        csv_row = ["CPU", "CPUCount", "", "2024-12-13T10:30:00", "16"]
        result = ESCPParser.parse_row(csv_row, is_identity=False)
        
        self.assertEqual(result.instance_no, "1")
    
    def test_parse_row_header_returns_none(self):
        """Test that header row returns None"""
        csv_row = ["METGROUP", "METRIC", "INSTANCE", "DATE", "VALUE"]
        result = ESCPParser.parse_row(csv_row, is_identity=True)
        
        self.assertIsNone(result)
    
    def test_parse_row_insufficient_columns_returns_none(self):
        """Test that row with too few columns returns None"""
        csv_row = ["HOSTNAME", "ServerName"]
        result = ESCPParser.parse_row(csv_row, is_identity=True)
        
        self.assertIsNone(result)


class TestCPUDetailsParser(unittest.TestCase):
    """Test CPU details parsing"""
    
    def test_parse_cpu_file_nonexistent(self):
        """Test handling of nonexistent file"""
        cpu_type, server_model = CPUDetailsParser.parse_cpu_file("/nonexistent/file.txt")
        
        self.assertEqual(cpu_type, "")
        self.assertEqual(server_model, "")
    
    @patch('builtins.open', create=True)
    def test_parse_cpu_file_valid(self, mock_open):
        """Test parsing valid CPU file"""
        mock_file = MagicMock()
        mock_file.readlines.return_value = [
            "CPU Type: Intel Xeon E5-2690\n",
            "Dell PowerEdge R630\n"
        ]
        mock_open.return_value.__enter__.return_value = mock_file
        
        cpu_type, server_model = CPUDetailsParser.parse_cpu_file("test.txt")
        
        self.assertEqual(cpu_type, "Intel Xeon E5-2690")
        self.assertEqual(server_model, "Dell PowerEdge R630")


class TestFileProcessor(unittest.TestCase):
    """Test file processing operations"""
    
    def test_validate_zip_file_nonexistent(self):
        """Test validation of nonexistent file"""
        result = FileProcessor.validate_zip_file("/nonexistent/file.zip")
        
        self.assertFalse(result)
    
    @patch('os.path.exists')
    @patch('zipfile.is_zipfile')
    def test_validate_zip_file_valid(self, mock_is_zipfile, mock_exists):
        """Test validation of valid zip file"""
        mock_exists.return_value = True
        mock_is_zipfile.return_value = True
        
        result = FileProcessor.validate_zip_file("test.zip")
        
        self.assertTrue(result)
    
    @patch('os.path.exists')
    @patch('zipfile.is_zipfile')
    def test_validate_zip_file_invalid_format(self, mock_is_zipfile, mock_exists):
        """Test validation of invalid zip file"""
        mock_exists.return_value = True
        mock_is_zipfile.return_value = False
        
        result = FileProcessor.validate_zip_file("test.txt")
        
        self.assertFalse(result)


class TestConfig(unittest.TestCase):
    """Test configuration"""
    
    def test_config_has_required_fields(self):
        """Test that config has all required fields"""
        self.assertIsNotNone(CONFIG.DB_USER)
        self.assertIsNotNone(CONFIG.DB_HOST)
        self.assertIsNotNone(CONFIG.DB_NAME)
        self.assertIsNotNone(CONFIG.TEMP_DIR)
    
    def test_config_date_formats(self):
        """Test that config has date formats"""
        self.assertIsInstance(CONFIG.DATE_FORMATS, list)
        self.assertGreater(len(CONFIG.DATE_FORMATS), 0)
    
    def test_config_batch_size_positive(self):
        """Test that batch size is positive"""
        self.assertGreater(CONFIG.BATCH_SIZE, 0)


if __name__ == '__main__':
    unittest.main()
