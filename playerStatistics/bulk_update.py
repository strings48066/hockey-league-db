import csv
import psycopg2

def update_player_statistics_from_csv(file_path):
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
                update_stat_query = """
                UPDATE PlayerStatistics
                SET GamesPlayed = %s,
                    Goals = %s,
                    Assists = %s,
                    PenaltyMinutes = %s
                WHERE SeasonID = %s AND PlayerID = %s AND TeamID = %s
                """
                cur.execute(update_stat_query, (
                    row['GamesPlayed'],
                    row['Goals'],
                    row['Assists'],
                    row['PenaltyMinutes'],
                    row['SeasonID'],
                    row['PlayerID'],
                    row['TeamID']
                ))

        # Commit the transaction
        conn.commit()

        print("Player statistics updated successfully")

    except Exception as e:
        # Rollback the transaction in case of error
        conn.rollback()
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()

if __name__ == "__main__":
    csv_file_path = '/path/to/player_statistics_update.csv'
    update_player_statistics_from_csv(csv_file_path)