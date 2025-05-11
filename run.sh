#!/bin/bash

echo ">>> Step 1: Running backend dependency setup"
python download_dependencies.py

if [ $? -ne 0 ]; then
  echo "Failed to run download_dependencies.py"
  exit 1
fi

echo ">>> Step 2: Installing frontend dependencies"
cd frontend || exit 1

npm install

if [ $? -ne 0 ]; then
  echo "npm install failed"
  exit 1
fi

echo ">>> Step 3: Starting frontend"
npm run start