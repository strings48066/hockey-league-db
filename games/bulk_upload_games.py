import csv
import psycopg2

def load_games_from_csv(file_path):
    try:
        conn = psycopg2.connect(
            dbname="uhl_db",
            user="uhl_user",
            password="uhl_password",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        conn.autocommit = False

        with open(file_path, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                Ref1 = row['Ref1'] if row['Ref1'].strip() else None
                Ref2 = row['Ref2'] if row['Ref2'].strip() else None

                insert_game_query = """
                INSERT INTO Games (SeasonID, Date, Time, Ref1, Ref2, HomeTeamID, AwayTeamID, HomeScore, AwayScore)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
                """
                cur.execute(insert_game_query, (
                    row['SeasonID'],
                    row['Date'],
                    row['Time'],
                    Ref1,
                    Ref2,
                    row['HomeTeamID'],
                    row['AwayTeamID'],
                    row['HomeScore'] if row['HomeScore'] else None,
                    row['AwayScore'] if row['AwayScore'] else None
                ))

        conn.commit()
        print("Games loaded successfully")

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")

    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    csv_file_path = 'input.csv'
    load_games_from_csv(csv_file_path)