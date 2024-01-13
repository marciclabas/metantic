#!/bin/bash
echo "Running 'chmod +x build.sh'"
chmod +x build.sh
echo "Running 'chmod +x frontend.sh'"
chmod +x frontend.sh
echo "Running 'python3.11 -m venv .venv'"
python3.11 -m venv .venv
source .venv/bin/activate
echo "Installing requirements.txt"
pip install --upgrade pip
pip install -r requirements.txt
echo "Uncomment requirements.txt to add moveread libs"
echo "Run 'source .venv/bin/activate' to activate"
echo "Edit pyproject.toml and run './build.sh' to build the package"
echo "Run './frontend.sh' to create a simple React frontend"
