from db_manager import get_db

db = get_db()



def get_all_participants():
    with db:
        df = db.query_df("SELECT participant_id FROM raw.participants;")
        return df

def create_allocations_table():
    with db:
        query = """
        CREATE TABLE IF NOT EXISTS raw.allocations (
            participant_id INTEGER PRIMARY KEY,
            classroom_id INTEGER DEFAULT 0
        );
        """
        db.execute_query(query)



def populate_allocations_table():
    participants_df = get_all_participants()
    if participants_df is None or participants_df.empty:
        print("No participants found.")
        return

    data = [(str(pid), 0) for pid in participants_df['participant_id']]

    with db:
        query = """
        INSERT INTO raw.allocations (participant_id, classroom_id)
        VALUES (%s, %s)
        ON CONFLICT (participant_id) DO NOTHING;
        """
        db.execute_many(query, data)


create_allocations_table()
populate_allocations_table()
