import csv
import psycopg2

def load_games_from_csv(file_path):
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
                insert_game_query = """
                INSERT INTO Games (SeasonID, Date, HomeTeamID, AwayTeamID, HomeScore, AwayScore)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cur.execute(insert_game_query, (
                    row['SeasonID'],
                    row['Date'],
                    row['HomeTeamID'],
                    row['AwayTeamID'],
                    row['HomeScore'],
                    row['AwayScore']
                ))

        # Commit the transaction
        conn.commit()
        print("Games loaded successfully")

    except Exception as e:
        # Rollback the transaction in case of error
        conn.rollback()
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()

if __name__ == "__main__":
    csv_file_path = '/path/to/games.csv'
    load_games_from_csv(csv_file_path)