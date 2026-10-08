"""Pytest configuration and fixtures."""
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment
os.environ["ENVIRONMENT"] = "development"
os.environ["SECRET_KEY"] = "test-secret-key-minimum-32-characters-long"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
