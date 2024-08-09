import csv
import psycopg2

def load_team_records_from_csv(file_path):
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
                insert_record_query = """
                INSERT INTO TeamRecords (SeasonID, TeamID, Wins, Losses, Ties)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (SeasonID, TeamID) DO NOTHING;
                """
                cur.execute(insert_record_query, (
                    row['SeasonID'],
                    row['TeamID'],
                    row['Wins'],
                    row['Losses'],
                    row['Ties']
                ))

        # Commit the transaction
        conn.commit()

        print("Team records loaded successfully")

    except Exception as e:
        # Rollback the transaction in case of error
        conn.rollback()
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()

if __name__ == "__main__":
    csv_file_path = '/path/to/team_records.csv'
    load_team_records_from_csv(csv_file_path)