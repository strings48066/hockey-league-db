import csv
import psycopg2

def update_players_from_csv(file_path):
    try:
        conn = psycopg2.connect(
            dbname="uhl_db",
            user="uhl_user",
            password="uhl_password",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        with open(file_path, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                jersey_number = row['JerseyNumber']
                player_id = row['PlayerID']
                
                if jersey_number and player_id:
                    update_query = """
                    UPDATE Players
                    SET JerseyNumber = %s
                    WHERE PlayerID = %s;
                    """
                    cursor.execute(update_query, (jersey_number, player_id))

        conn.commit()
        print("Players updated successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_players_from_csv('input.csv')