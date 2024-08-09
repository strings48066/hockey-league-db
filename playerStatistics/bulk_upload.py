import csv
import psycopg2

def load_player_statistics_from_csv(file_path):
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
                insert_stat_query = """
                INSERT INTO PlayerStatistics (SeasonID, PlayerID, TeamID, GamesPlayed, Goals, Assists, PenaltyMinutes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (SeasonID, PlayerID) DO NOTHING;
                """
                cur.execute(insert_stat_query, (
                    row['SeasonID'],
                    row['PlayerID'],
                    row['TeamID'],
                    row['GamesPlayed'],
                    row['Goals'],
                    row['Assists'],
                    row['PenaltyMinutes']
                ))

        # Commit the transaction
        conn.commit()

        print("Player statistics loaded successfully")

    except Exception as e:
        # Rollback the transaction in case of error
        conn.rollback()
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()

if __name__ == "__main__":
    csv_file_path = '/path/to/player_statistics.csv'
    load_player_statistics_from_csv(csv_file_path)