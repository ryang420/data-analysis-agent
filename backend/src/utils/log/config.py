"""
Application configuration
"""
import os
from pathlib import Path

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

LOG_DIR = Path(os.getenv("APP_LOG_DIR", "/tmp/work/logs/bypass"))
