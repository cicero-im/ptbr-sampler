#!/usr/bin/env python
"""
Entry point script to run the ptbr-sampler CLI.

This script provides a convenient way to run the CLI without worrying about
Python package paths or import issues.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import and run the CLI
from ptbr_sampler import run_cli

if __name__ == "__main__":
    run_cli() 