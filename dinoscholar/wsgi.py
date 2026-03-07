"""
WSGI entry point for PythonAnywhere deployment.

PythonAnywhere WSGI configuration should point to this file:
    /home/<username>/DinoScholar/dinoscholar/wsgi.py

And set the "Source code" directory to:
    /home/<username>/DinoScholar/dinoscholar
"""

import sys
import os

# Ensure the application package directory is on sys.path so that
# imports like "from database import db" resolve correctly.
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from app import create_app  # noqa: E402

application = create_app()
