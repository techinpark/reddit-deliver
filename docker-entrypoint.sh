#!/bin/bash
set -e

echo "Initializing reddit-deliver..."

# Initialize database from environment variables
python -m cli.init_from_env

echo "Starting monitoring service..."

# Execute the main command
exec "$@"
