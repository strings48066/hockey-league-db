import csv
import psycopg2

def update_team_records_from_csv(file_path):
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
                update_record_query = """
                UPDATE TeamRecords
                SET Wins = %s,
                    Losses = %s,
                    Ties = %s
                WHERE SeasonID = %s AND TeamID = %s
                """
                cur.execute(update_record_query, (
                    row['Wins'],
                    row['Losses'],
                    row['Ties'],
                    row['SeasonID'],
                    row['TeamID']
                ))

        # Commit the transaction
        conn.commit()

        print("Team records updated successfully")

    except Exception as e:
        # Rollback the transaction in case of error
        conn.rollback()
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()

if __name__ == "__main__":
    csv_file_path = '/path/to/team_records_update.csv'
    update_team_records_from_csv(csv_file_path)