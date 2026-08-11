"""Streamlit entrypoint: runs the maps dashboard in app_mapas.py."""
import os
import runpy
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
runpy.run_path(os.path.join(os.path.dirname(__file__), "app_mapas.py"), run_name="__main__")