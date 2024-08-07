# Hockey League Database

This repository contains the setup and scripts to manage the Ultimate Hockey League database, including the schema, Docker setup, and bulk upload scripts.

## Table of Contents

- [Setup](#setup)
- [Database Schema](#database-schema)
- [Running with Docker](#running-with-docker)
- [Bulk Upload](#bulk-upload)
- [Contributing](#contributing)
- [License](#license)

## Setup

1. **Clone the Repository**
    ```sh
    git clone https://github.com/strings48066/hockey-league-db.git
    cd hockey-league-db
    ```

2. **Set up Environment Variables**
    Create a `.env` file with the following content:
    ```env
    POSTGRES_DB=uhl_db
    POSTGRES_USER=uhl_user
    POSTGRES_PASSWORD=uhl_password
    ```

## Database Schema

The database schema is defined in `sql_scripts/setup.sql`. This script creates the necessary tables for managing teams, players, statistics, and more.

## Running with Docker

1. **Start Services**
    ```sh
    docker-compose up -d
    ```

2. **Initialize the Database**
    ```sh
    docker exec -i <container_id> psql -U uhl_user -d uhl_db < sql_scripts/setup.sql
    ```

## Bulk Upload

### Bulk Upload Players

1. **CSV Format**
    Create a CSV file `players.csv` with the following columns:
    ```csv
    FirstName,LastName,Position,JerseyNumber,Email
    Alice,Johnson,Forward,9,alice.johnson@example.com
    Bob,Smith,Defenseman,23,bob.smith@example.com
    ```

2. **Run Bulk Upload Script**
    ```sh
    python3 python_scripts/bulk_upload_players.py /path/to/players.csv
    ```

### Bulk Upload Player Statistics

1. **CSV Format**
    Create a CSV file `player_statistics.csv` with the following columns:
    ```csv
    SeasonID,PlayerID,TeamID,GamesPlayed,Goals,Assists,PenaltyMinutes
    2,1,5,12,5,10,6
    2,2,5,10,3,7,4
    ```

2. **Run Bulk Upload Script**
    ```sh
    python3 python_scripts/bulk_upload_player_statistics.py /path/to/player_statistics.csv
    ```

## Contributing

Feel free to open issues or submit pull requests with improvements.
