"""
Configuration management for IParking automation system.
"""

import os
from typing import Dict, Any


class Config:
    """Configuration class for IParking automation."""
    
    def __init__(self):
        """Initialize configuration with default values."""
        self.base_url = "http://members.iparking.co.kr"
        self.test_account = {
            "username": "dtctrit2704",
            "password": "dtctrit2704"
        }
        self.test_vehicle = "1255"
        
        # WebDriver settings
        self.chrome_options = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1920,1080"
        ]
        
        # Timeout settings
        self.implicit_wait = 10
        self.page_load_timeout = 30
        self.element_wait_timeout = 10
        
        # Logging settings
        self.log_level = "INFO"
        self.log_format = "%(asctime)s - %(levelname)s - %(message)s"
    
    def get_chrome_options(self, headless: bool = False) -> list:
        """Get Chrome options list."""
        options = self.chrome_options.copy()
        if headless:
            options.append("--headless")
        return options
    
    def update_from_env(self):
        """Update configuration from environment variables."""
        self.base_url = os.getenv("IPARKING_BASE_URL", self.base_url)
        self.test_account["username"] = os.getenv("IPARKING_USERNAME", self.test_account["username"])
        self.test_account["password"] = os.getenv("IPARKING_PASSWORD", self.test_account["password"])
        self.test_vehicle = os.getenv("IPARKING_TEST_VEHICLE", self.test_vehicle)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "base_url": self.base_url,
            "test_account": self.test_account,
            "test_vehicle": self.test_vehicle,
            "chrome_options": self.chrome_options,
            "implicit_wait": self.implicit_wait,
            "page_load_timeout": self.page_load_timeout,
            "element_wait_timeout": self.element_wait_timeout,
            "log_level": self.log_level,
            "log_format": self.log_format
        }
