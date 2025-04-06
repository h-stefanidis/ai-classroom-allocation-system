# Not finalised - will use this as a template for the setup script towards end of the project.
# This script sets up the ClassForge project environment.

#!/bin/bash

echo "Setting up ClassForge..."

# Python backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# React frontend setup
cd frontend
npm install
cd ..

# Optional: setup Neo4j/PostgreSQL, e.g., Docker setup or local start

echo "Setup complete."
