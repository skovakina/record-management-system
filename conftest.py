"""Test configuration: make ``src`` importable so tests can ``import record``."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
