"""
Helper utilities for IParking automation system.
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime


def setup_logging(level: str = "INFO", format_string: Optional[str] = None) -> logging.Logger:
    """Setup logging configuration."""
    if format_string is None:
        format_string = "%(asctime)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string
    )
    
    return logging.getLogger(__name__)


def measure_time(func):
    """Decorator to measure function execution time."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        
        logger = logging.getLogger(func.__module__)
        logger.info(f"{func.__name__} 실행 시간: {execution_time:.2f}초")
        
        if isinstance(result, dict):
            result['execution_time'] = execution_time
        
        return result
    return wrapper


def format_timestamp(timestamp: Optional[float] = None) -> str:
    """Format timestamp to readable string."""
    if timestamp is None:
        timestamp = time.time()
    
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary."""
    try:
        return dictionary[key]
    except (KeyError, TypeError):
        return default


def validate_vehicle_number(vehicle_number: str) -> bool:
    """Validate vehicle number format."""
    if not vehicle_number:
        return False
    
    # Basic validation: should be numeric and 4 digits
    return vehicle_number.isdigit() and len(vehicle_number) == 4


def validate_account_info(account_info: Dict[str, str]) -> bool:
    """Validate account information."""
    required_fields = ["username", "password"]
    
    for field in required_fields:
        if field not in account_info or not account_info[field]:
            return False
    
    return True


def create_result_dict(success: bool, **kwargs) -> Dict[str, Any]:
    """Create standardized result dictionary."""
    result = {
        "success": success,
        "timestamp": time.time(),
        "timestamp_formatted": format_timestamp()
    }
    
    result.update(kwargs)
    return result


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry function on failure."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger = logging.getLogger(func.__module__)
                        logger.warning(f"{func.__name__} 실패 (시도 {attempt + 1}/{max_retries}): {e}")
                        time.sleep(delay)
                    else:
                        logger = logging.getLogger(func.__module__)
                        logger.error(f"{func.__name__} 최종 실패: {e}")
            
            raise last_exception
        return wrapper
    return decorator
