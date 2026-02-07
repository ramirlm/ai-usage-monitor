#!/bin/bash
# Quick start script for AI Usage Monitor Dashboard

set -e

echo "🚀 AI Usage Monitor Dashboard - Quick Start"
echo "=========================================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3.7+"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if in correct directory
if [ ! -d "backend" ]; then
    echo "❌ Please run this script from the ai-usage-monitor root directory"
    exit 1
fi

cd backend

# Check if database exists
if [ ! -f "ai-usage.db" ]; then
    echo ""
    echo "📦 Database not found. Initializing..."
    python3 cli.py init
    echo "✓ Database initialized"
    
    echo ""
    echo "📊 Would you like to generate sample data for testing? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Generating sample data..."
        python3 generate_sample_data.py
        echo "✓ Sample data generated"
    fi
else
    echo "✓ Database found"
fi

# Check if dependencies are installed
echo ""
echo "📦 Checking dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip3 install -q -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

echo ""
echo "=========================================="
echo "🎉 Starting Dashboard..."
echo "=========================================="
echo ""
echo "Dashboard will be available at:"
echo "  👉 http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the dashboard
python3 cli.py dashboard
