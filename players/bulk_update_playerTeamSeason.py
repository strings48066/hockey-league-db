import csv
import psycopg2

def bulk_update_player_team_seasons(file_path):
    """
    Updates the PlayerTeamSeasons table in the database with data from a CSV file.

    Args:
        file_path (str): The path to the CSV file containing player team season data.

    The CSV file should have the following columns:
        - PlayerID
        - TeamID
        - SeasonID
        - IsCurrent

    The function will update the PlayerTeamSeasons table based on the PlayerID, TeamID, and SeasonID provided in the CSV file.
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(
            dbname="uhl_db",
            user="uhl_user",
            password="uhl_password",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        # Begin transaction
        conn.autocommit = False

        # Open the CSV file
        with open(file_path, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                update_query = """
                INSERT INTO PlayerTeamSeasons (PlayerID, TeamID, SeasonID, IsCurrent)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (PlayerID, TeamID, SeasonID)
                DO UPDATE SET IsCurrent = EXCLUDED.IsCurrent;
                """
                cur.execute(update_query, (
                    row['PlayerID'],
                    row['TeamID'],
                    row['SeasonID'],
                    row['IsCurrent']
                ))

        # Commit the transaction
        conn.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

# Example usage
file_path = 'player_team_seasons.csv'
bulk_update_player_team_seasons(file_path)