#!/usr/bin/env python3
"""
Enhanced Sizing and Provisioning (ESP) Processor
Main application entry point
"""
import sys
import logging
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from config import CONFIG
from orchestrator import ESPOrchestrator

# Configure logging
def setup_logging(verbose: bool = False):
    """
    Setup logging configuration
    
    Args:
        verbose: Enable verbose (DEBUG) logging
    """
    log_level = logging.DEBUG if verbose else getattr(logging, CONFIG.LOG_LEVEL)
    
    # Create formatters
    file_formatter = logging.Formatter(CONFIG.LOG_FORMAT)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    
    # Setup file handler
    file_handler = logging.FileHandler(CONFIG.LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Silence noisy third-party loggers
    logging.getLogger('mysql.connector').setLevel(logging.WARNING)


def create_argument_parser() -> ArgumentParser:
    """
    Create and configure argument parser
    
    Returns:
        Configured ArgumentParser
    """
    banner = f"""
{CONFIG.APP_DESC}
Version: {CONFIG.APP_VERSION} ({CONFIG.APP_VERSION_DATE})
Status: {CONFIG.APP_STATE}
    """
    
    parser = ArgumentParser(
        description=banner,
        formatter_class=RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -c 12345                    # Process collection 12345
  %(prog)s -c 12345 -v                 # Process with verbose output
  %(prog)s --version                   # Show version information
  %(prog)s -c 12345 --dry-run          # Validate without processing
        """
    )
    
    parser.add_argument(
        '-c', '--collection',
        dest='collection_id',
        type=str,
        required=True,
        help='Collection ID to process (required)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='Enable verbose (DEBUG) logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {CONFIG.APP_VERSION} ({CONFIG.APP_VERSION_DATE})'
    )
    
    parser.add_argument(
        '--dry-run',
        dest='dry_run',
        action='store_true',
        default=False,
        help='Validate configuration without processing files'
    )
    
    parser.add_argument(
        '--log-file',
        dest='log_file',
        type=str,
        default=CONFIG.LOG_FILE,
        help=f'Log file path (default: {CONFIG.LOG_FILE})'
    )
    
    return parser


def validate_environment() -> bool:
    """
    Validate environment and configuration
    
    Returns:
        True if valid, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    # Check temp directory
    try:
        import os
        os.makedirs(CONFIG.TEMP_DIR, exist_ok=True)
        logger.info(f"Temp directory: {CONFIG.TEMP_DIR}")
    except Exception as e:
        logger.error(f"Cannot create temp directory: {e}")
        return False
    
    # Check database configuration
    if not all([CONFIG.DB_USER, CONFIG.DB_HOST, CONFIG.DB_NAME]):
        logger.error("Incomplete database configuration")
        return False
    
    logger.info(f"Database: {CONFIG.DB_NAME}@{CONFIG.DB_HOST}")
    return True


def main():
    """Main application entry point"""
    
    # Parse arguments
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Update log file if specified
    if args.log_file:
        CONFIG.LOG_FILE = args.log_file
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("="*60)
    logger.info(f"{CONFIG.APP_DESC} v{CONFIG.APP_VERSION}")
    logger.info("="*60)
    
    # Validate environment
    if not validate_environment():
        logger.error("Environment validation failed")
        return 1
    
    # Dry run mode
    if args.dry_run:
        logger.info("DRY RUN MODE - No files will be processed")
        logger.info(f"Collection ID: {args.collection_id}")
        logger.info("Configuration validated successfully")
        return 0
    
    # Process collection
    exit_code = 0
    try:
        orchestrator = ESPOrchestrator()
        stats = orchestrator.process_collection(args.collection_id)
        
        # Print final statistics
        logger.info("="*60)
        logger.info("PROCESSING COMPLETE")
        logger.info("="*60)
        logger.info(str(stats))
        
        # Set exit code based on results
        if stats.failed_files > 0:
            exit_code = 2  # Partial failure
        elif stats.successful_files == 0:
            exit_code = 1  # Complete failure
        
        # Print errors if any
        if stats.errors:
            logger.error("\nErrors encountered:")
            for i, error in enumerate(stats.errors, 1):
                logger.error(f"  {i}. {error}")
        
    except KeyboardInterrupt:
        logger.warning("\nProcessing interrupted by user")
        exit_code = 130
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        exit_code = 1
    
    logger.info("="*60)
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
