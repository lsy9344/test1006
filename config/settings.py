"""
Settings management for IParking automation system.
"""

import os
from typing import Dict, Any, Optional


class Settings:
    """Global settings management."""
    
    def __init__(self):
        """Initialize settings."""
        self.project_name = "IParking Automation System"
        self.version = "1.0.0"
        self.debug = False
        
        # Paths
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.project_root, "data")
        self.docs_dir = os.path.join(self.project_root, "docs")
        self.tests_dir = os.path.join(self.project_root, "tests")
        
        # API settings
        self.api_timeout = 30
        self.max_retries = 3
        self.retry_delay = 1
        
        # Web server settings
        self.web_host = "localhost"
        self.web_port = 5000
        self.web_debug = False
    
    def get_data_path(self, filename: str) -> str:
        """Get full path for data file."""
        return os.path.join(self.data_dir, filename)
    
    def get_docs_path(self, filename: str) -> str:
        """Get full path for docs file."""
        return os.path.join(self.docs_dir, filename)
    
    def get_tests_path(self, filename: str) -> str:
        """Get full path for test file."""
        return os.path.join(self.tests_dir, filename)
    
    def update_from_env(self):
        """Update settings from environment variables."""
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.api_timeout = int(os.getenv("API_TIMEOUT", str(self.api_timeout)))
        self.max_retries = int(os.getenv("MAX_RETRIES", str(self.max_retries)))
        self.web_host = os.getenv("WEB_HOST", self.web_host)
        self.web_port = int(os.getenv("WEB_PORT", str(self.web_port)))
        self.web_debug = os.getenv("WEB_DEBUG", "false").lower() == "true"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "project_name": self.project_name,
            "version": self.version,
            "debug": self.debug,
            "project_root": self.project_root,
            "data_dir": self.data_dir,
            "docs_dir": self.docs_dir,
            "tests_dir": self.tests_dir,
            "api_timeout": self.api_timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "web_host": self.web_host,
            "web_port": self.web_port,
            "web_debug": self.web_debug
        }


# Global settings instance
settings = Settings()
