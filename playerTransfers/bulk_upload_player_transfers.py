import csv
import psycopg2

def load_player_transfers_from_csv(file_path):
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
                insert_transfer_query = """
                INSERT INTO PlayerTransfers (PlayerID, FromTeamID, ToTeamID, TransferDate)
                VALUES (%s, %s, %s, %s)
                """
                cur.execute(insert_transfer_query, (
                    row['PlayerID'],
                    row['FromTeamID'],
                    row['ToTeamID'],
                    row['TransferDate']
                ))

        # Commit the transaction
        conn.commit()
        print("Player transfers loaded successfully")

    except Exception as e:
        # Rollback the transaction in case of error
        conn.rollback()
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()

if __name__ == "__main__":
    csv_file_path = '/path/to/player_transfers.csv'
    load_player_transfers_from_csv(csv_file_path)