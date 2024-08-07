#!/bin/bash

# Start Docker Compose
echo "Starting PostgreSQL container..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until docker exec uhl_postgres_db pg_isready -U uhl_user; do
  sleep 1
done

# Run the SQL script to create tables and insert data
echo "Running setup SQL script..."
docker exec -i uhl_postgres_db psql -U uhl_user -d uhl_db < setup.sql

echo "Database setup complete."