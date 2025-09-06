#!/bin/bash

# Script to setup PostGIS for SmartLeakPro
# This script should be run on the database server

echo "Setting up PostGIS for SmartLeakPro..."

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "Error: PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

# Check if PostGIS is already installed
if psql -d postgres -c "SELECT 1 FROM pg_extension WHERE extname = 'postgis';" | grep -q "1 row"; then
    echo "PostGIS is already installed."
else
    echo "Installing PostGIS extension..."
    
    # Install PostGIS extension
    psql -d postgres -c "CREATE EXTENSION IF NOT EXISTS postgis;"
    psql -d postgres -c "CREATE EXTENSION IF NOT EXISTS postgis_topology;"
    
    if [ $? -eq 0 ]; then
        echo "PostGIS installed successfully."
    else
        echo "Error: Failed to install PostGIS. Please check your PostgreSQL installation."
        exit 1
    fi
fi

# Create the database if it doesn't exist
DB_NAME=${DB_NAME:-smartleakpro}
if ! psql -d postgres -c "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME';" | grep -q "1 row"; then
    echo "Creating database: $DB_NAME"
    createdb $DB_NAME
fi

# Enable PostGIS on the application database
echo "Enabling PostGIS on application database: $DB_NAME"
psql -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS postgis;"
psql -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS postgis_topology;"

echo "PostGIS setup completed successfully!"
echo "You can now run Django migrations to create the geospatial tables."
