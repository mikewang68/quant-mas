import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration paths
CONFIG_DIR = project_root / "config"
DATA_DIR = project_root / "data"
LOGS_DIR = project_root / "logs"

# Create directories if they don't exist
CONFIG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
