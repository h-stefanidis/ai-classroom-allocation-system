from .db_manager import get_db
# from ml.build_graph import build_graph_from_dataframe
import sys
from pathlib import Path
import hashlib
sys.path.append(str(Path(__file__).resolve().parent.parent))

# from db_manager import get_db
from ml.build_graph import build_graph_from_dataframe
from ml.export_clusters import export_clusters
from ml.cluster_with_gnn_with_constraints import cluster_constraints
from ml.evaluate_model import analyze_graph
#import ml.evaluate_model
import json
from db.db_manager import get_db
from pathlib import Path
import uuid
import jsonify

# Get Database reference
db = get_db()


# Get all participants from SupaBase
def get_all_participants_ids():
    with db:
        df = db.query_df("SELECT participant_id FROM raw.participants;")
        return df

def get_all_participants():
    with db:
        df = db.query_df("SELECT * FROM raw.participants;")
        return df
        
def get_all_allocations():
    with db:
        df = db.query_df("SELECT * FROM raw.allocations;")
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

def drop_allocations_table():
    try:
        with db:
            db.execute("DROP TABLE IF EXISTS raw.allocations;")
        return {"message": "Table 'raw.allocations' dropped successfully."}, 200
    except Exception as e:
        return {"error": f"Failed to drop table: {str(e)}"}, 500
    


# Populate new Allocations Table
def populate_allocations_table():
    participants_df = get_all_participants_ids()
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


def update_classroom_allocations(allocation_json):
    """
    Updates classroom IDs in raw.allocations for existing student IDs based on a JSON dictionary.
    Structure must be: { "Allocations": { "Classroom_X": [student_id, ...], ... } }
    """


    allocations = allocation_json.get("Allocations", {})
    if not allocations:
        return {"error": "No allocations found in JSON"}, 400

    # Prepare update values
    update_values = []
    for classroom_label, student_ids in allocations.items():
        classroom_id = classroom_label  # e.g., "Classroom_2" -> 2
        for student_id in student_ids:
            db.execute("""
                INSERT INTO raw.allocations (student_id, classroom)
                VALUES (%s, %s)
                ON CONFLICT (student_id) DO UPDATE
                SET classroom = EXCLUDED.classroom;
            """, (student_id, classroom_id))

    # Step 4: Insert new allocations
    insert_values = []
    for classroom_name, student_ids in allocations.items():
        classroom_number = int(classroom_name.split("_")[1])  # e.g., "Classroom_3" -> 3
        for student_id in student_ids:
            update_values.append((student_id, classroom_id))

    if not update_values:
        return {"error": "No valid student allocations found"}, 400

    # Perform upsert: insert or update classroom_id if student_id exists
    db.execute_many("""
        INSERT INTO raw.allocations (participant_id, classroom_id)
        VALUES (%s, %s)
        ON CONFLICT (participant_id) DO UPDATE
        SET classroom_id = EXCLUDED.classroom_id;
    """, update_values)

    return {"message": "Allocations updated successfully", "total_updated": len(update_values)}, 200

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

# For login and sign up
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()



def register_user(email, password, username, role="user"):
    password_hash = hash_password(password)

    with db:
        query = """
        INSERT INTO public.users (email, password_hash, username)
        VALUES (%s, %s, %s)
        ON CONFLICT (email) DO NOTHING;
        """
        db.execute_query(query, (email, password_hash, username))
    return {"success":True}



def login_user(email, password):
    password_hash = hash_password(password)

    query = """
    SELECT user_id, username, role 
    FROM public.users 
    WHERE email = %s AND password_hash = %s
    LIMIT 1;
    """

    with db:
        result = db.fetch_one(query, (email, password_hash))

    if result:
        user_id, username, role = result
        return {
            "user_id": user_id,
            "username": username,
            "role": role or "user"
        }
    return None


def classroom_update(participant_id: int, classroom_id: int):
    """
    Update the classroom for a given participant_id.
    If the participant_id doesn't exist, insert it.
    Returns a dict with operation status and relevant info.
    """
    try:
        db.execute("""
            INSERT INTO raw.allocations (student_id, classroom)
            VALUES (%s, %s)
            ON CONFLICT (student_id) DO UPDATE
            SET classroom = EXCLUDED.classroom;
        """, (participant_id, classroom_id))
        return {
            "status": "success",
            "participant_id": participant_id,
            "classroom_id": classroom_id
        }
    except Exception as e:
        return {
            "status": "failure",
            "participant_id": participant_id,
            "classroom_id": classroom_id,
            "error": str(e)
        }

def get_relationship_summary_by_run(run_number: str):
    query = """
        SELECT group_id, friend, influence, feedback, more_time, advice, disrespect
        FROM public.preserve_edge
        WHERE run_number = %s
    """
    with db:
        return db.query_df(query, (run_number,))
    

def get_all_allocation_run_numbers():
    query = """
        SELECT DISTINCT run_number
        FROM public.classroom_allocation
        ORDER BY run_number DESC;
    """
    with db:
        return db.query_df(query)

def inspect_clustered_graph():
    participants_df = get_all_participants()

def generate_run_number():
    return str(uuid.uuid4()) 

def fetch_student_dict_from_id(db, json_data):
    """
    {
    "Allocations": {
        "Classroom_1": [
            {
                "first_name": "Jeremiah",
                "last_name": "Murphy",
                "participant_id": 32394
            }]},
    ,
    "Total_Classrooms": 4,
    "Total_Students": 175
    """

    #At first save this allocation
    run_number = save_allocations_to_db(db, json_data )


    allocations = json_data["Allocations"]

    try:
        enriched = {}

        with db:
            for classroom, student_ids in allocations.items():
                query = f"""
                    SELECT participant_id, first_name, last_name
                    FROM raw.participants
                    WHERE participant_id = ANY(%s);
                """
                result = db.query_df(query, (student_ids,))

                enriched[classroom] = result.to_dict(orient="records")
        return {
            "Allocations": enriched,
            "Total_Classrooms": json_data["Total_Classrooms"],
            "Total_Students": json_data["Total_Students"],
            "Run_Number": run_number
        }

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def save_allocations_to_db(db, allocation_data: dict):
    run_number = generate_run_number()
    rows_to_insert = []

    for classroom_name, student_ids in allocation_data["Allocations"].items():
        for student_id in student_ids:
            rows_to_insert.append((run_number, classroom_name, student_id))

    query = """
    INSERT INTO public.classroom_allocation (run_number, classroom_id, participant_id)
    VALUES (%s, %s, %s)
    """

    with db:
        db.execute_many(query, rows_to_insert)

    print(f"Inserted {len(rows_to_insert)} rows for run {run_number}")
    return run_number