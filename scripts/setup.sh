#!/bin/bash
set -e

echo "========================================="
echo "   AttendX Development Setup"
echo "========================================="

# Check Python version
echo ""
echo "Checking Python version..."
python --version || { echo "Error: Python not found. Please install Python 3.10+"; exit 1; }

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate 2>/dev/null || { echo "Error: Could not activate virtual environment"; exit 1; }

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment variables
echo ""
echo "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ".env file created from .env.example"
    echo "Please edit .env with your settings"
else
    echo ".env file already exists."
fi

# Run migrations
echo ""
echo "Running migrations..."
python manage.py migrate

# Create superuser
echo ""
echo "Creating admin superuser..."
python manage.py seed_data

echo ""
echo "========================================="
echo "   Setup Complete!"
echo "========================================="
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Admin login: admin / admin123"
echo "========================================="
