"""
Core module for IParking automation system.

This module contains the main automation classes and configuration management.
"""

from .automation import IParkingAutomation
from .config import Config

__all__ = ['IParkingAutomation', 'Config']
