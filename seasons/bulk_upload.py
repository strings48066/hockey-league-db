import csv
import psycopg2

def load_seasons_from_csv(file_path):
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
                insert_season_query = """
                INSERT INTO Seasons (Year)
                VALUES (%s)
                ON CONFLICT DO NOTHING;
                """
                cur.execute(insert_season_query, (
                    row['Year'],
                ))

        # Commit the transaction
        conn.commit()

        print("Seasons loaded successfully")

    except Exception as e:
        # Rollback the transaction in case of error
        conn.rollback()
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()

if __name__ == "__main__":
    csv_file_path = 'input.csv'
    load_seasons_from_csv(csv_file_path)