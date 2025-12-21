#!/bin/bash

echo "Starting Meat Bro Discord Bot..."
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if python-dotenv is installed
python3 -m pip show python-dotenv > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "python-dotenv not found. Installing..."
    pip install python-dotenv
fi

echo "Running bot..."
python3 bot.py
