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
### Database Table Load Order

When setting up a new database, follow this load order to respect foreign key dependencies:

1. **Seasons**
   - No dependencies. Create and load this first.

2. **Teams**
   - No dependencies. Create and load this second.

3. **Players**
   - Depends on `Teams` (`TeamID`). Load after Teams.

4. **TeamSeasons**
   - Links `Teams` to `Seasons` (`TeamID`, `SeasonID`). Load after both Teams and Seasons.

5. **Games**
   - Depends on `Teams` and `Seasons` (`HomeTeamID`, `AwayTeamID`, `SeasonID`). Load after Teams and Seasons.

6. **GameEvents**
   - Depends on `Games` and `Players` (`GameID`, `PlayerID`). Load after Games and Players.

By following this order, all foreign key constraints will be properly handled as you populate your database.

# Backup and Restore Procedures

## Backup Procedure

1. **Start the Database**
   - **Command**: `docker-compose up -d db`
   - **Purpose**: Ensures the PostgreSQL container is running.

2. **Run the Backup**
   - **Command**: `docker-compose run backup`
   - **Purpose**: Creates a timestamped backup file in the `./backup` directory.

3. **Verify Backup**
   - **Check**: Look for the `.backup` file in the `./backup` directory.

4. **Store Backup Securely**
   - **Option**: Upload to a secure location (e.g., AWS S3).

## Restore Procedure

1. **Ensure the Database is Running**
   - **Command**: `docker-compose up -d db`

2. **Run the Restore**
   - **Command**: `docker-compose run restore`
   - **Note**: Replace `your_backup_file.backup` with the specific backup file name.

3. **Verify Restoration**
   - **Check**: Ensure the data has been correctly restored in the database.

4. **Cleanup**
   - **Option**: Remove unnecessary backup files if needed.

## Contributing
Feel free to open issues or submit pull requests with improvements.
