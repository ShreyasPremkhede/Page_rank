#!/bin/bash

# Create venv directory if it doesn't exist
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip (optional but recommended)
python -m pip install --upgrade pip

# Install dependencies from requirements.txt
pip install -r requirements.txt