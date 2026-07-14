#!/bin/sh
set -e

# Upgrade pip in the base interpreter
python -m pip install --upgrade pip

# Remove old virtual environment
rm -rf .venv

# Create & activate venv
python -m venv .venv

# POSIX "source"
. .venv/bin/activate

# Upgrade pip in the venv
python -m pip install --upgrade pip

# Install your project (dev extras) into the venv (NO --user)
pip install --editable ".[dev]"

# Ensure pre-commit is available (either in [dev] or install here)
# pip install pre-commit  # uncomment if not in [dev]
pre-commit install
