# Start from the official Python Dev Container base image
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Upgrade pip
RUN pip install --upgrade pip

# Add the user install directory to path
ENV PATH="/home/vscode/.local/bin:$PATH"
