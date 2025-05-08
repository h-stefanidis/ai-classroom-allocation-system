from .db_manager import get_db
# from ml.build_graph import build_graph_from_dataframe
import json
from pathlib import Path


# Get Database reference
db = get_db()


# Get all participants from SupaBase
def get_all_participants():
    with db:
        df = db.query_df("SELECT participant_id FROM raw.participants;")
        return df


# Create Allocations Table (Column 1: ID, Column 2: Classroom Allocation)
def create_allocations_table():
    with db:
        query = """
        CREATE TABLE IF NOT EXISTS raw.allocations (
            participant_id INTEGER PRIMARY KEY,
            classroom_id INTEGER DEFAULT 0
        );
        """
        db.execute_query(query)


# Populate new Allocations Table
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


def classroom_allocation_update():
    # Step 1: Load participant dataframe (if needed elsewhere)
    participants_df = get_all_participants()
    build_graph_from_dataframe(participants_df)

    # Step 2: Load JSON file
    json_path = Path("ml/classforge_project/SchoolData/data/classroom_allocations.json")
    with open(json_path, "r") as f:
        allocation_data = json.load(f)

    allocations = allocation_data["Allocations"]

    # Step 3: Clear old allocations (optional, depending on your use case)
    db.execute("DELETE FROM raw.allocations")

    # Step 4: Insert new allocations
    insert_values = []
    for classroom_name, student_ids in allocations.items():
        classroom_number = int(classroom_name.split("_")[1])  # e.g., "Classroom_3" -> 3
        for student_id in student_ids:
            insert_values.append((student_id, classroom_number))

    # Step 5: Perform batch insert
    db.bulk_insert(
        table="raw.allocations",
        columns=["student_id", "classroom"],
        values=insert_values
    )

    return {"message": "Allocations updated", "total": len(insert_values)}

def get_all_participants():
    with db:
        df = db.query_df("SELECT * FROM raw.participants;")
        return df

def get_all_more_time():
    with db:
        df = db.query_df("SELECT * FROM raw.more_time;")
        return df

def get_all_influential():
    with db:
        df = db.query_df("SELECT * FROM raw.influential;")
        return df

def get_all_friends():
    with db:
        df = db.query_df("SELECT * FROM raw.friends;")
        return df

def get_all_feedback():
    with db:
        df = db.query_df("SELECT * FROM raw.feedback;")
        return df

def get_all_advice():
    with db:
        df = db.query_df("SELECT * FROM raw.feedback;")
        return df

def get_all_disrespect():
    with db:
        df = db.query_df("SELECT * FROM raw.disrespect;")
        return df


# TODO: Move out of file?
# create_allocations_table()
# populate_allocations_table()
