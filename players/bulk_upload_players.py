import csv
import psycopg2

def load_players_from_csv(file_path):
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
                # Convert empty strings to None
                jersey_number = row['JerseyNumber'] if row['JerseyNumber'] else None

                insert_user_query = """
                INSERT INTO Players (FirstName, LastName, Position, JerseyNumber, Email)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (Email) DO UPDATE
                SET FirstName = EXCLUDED.FirstName,
                    LastName = EXCLUDED.LastName,
                    Position = EXCLUDED.Position,
                    JerseyNumber = EXCLUDED.JerseyNumber;
                """
                cur.execute(insert_user_query, (
                    row['FirstName'],
                    row['LastName'],
                    row['Position'],
                    jersey_number,
                    row['Email']
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
csv_file_path = 'input.csv'
load_players_from_csv(csv_file_path)