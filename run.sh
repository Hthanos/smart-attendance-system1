#!/bin/bash
# Smart Class Attendance System - Launch Script

echo "=================================================="
echo "  Smart Class Attendance System"
echo "  Moi University - Department of EEE"
echo "=================================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
    echo ""
fi

# Activate virtual environment
source venv/bin/activate

# Check if database exists
if [ ! -f "data/database/attendance.db" ]; then
    echo "Initializing database..."
    python -m src.database.db_manager
    echo ""
fi

# Run application
echo "Starting application..."
echo ""
python app.py

# Deactivate virtual environment on exit
deactivate
