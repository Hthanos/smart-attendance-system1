#!/bin/bash
# Quick start script for Smart Class Attendance System

# Activate virtual environment
source venv/bin/activate

# Set library path for OpenCV
export LD_LIBRARY_PATH=$HOME/.local/lib/python3.13/site-packages/opencv_contrib_python.libs:$LD_LIBRARY_PATH

# Run application
python app.py
