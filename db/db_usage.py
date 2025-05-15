import sys
from pathlib import Path
import hashlib
sys.path.append(str(Path(__file__).resolve().parent.parent))
from db.db_manager import get_db
from pathlib import Path
import uuid
<<<<<<< HEAD
from sqlalchemy import text

=======
from flask import jsonify
>>>>>>> f50ae4a424232c8476de2cecd9cd2801bfc3d1f5

# Get Database reference
db = get_db()


# Get all participants from SupaBase
def get_all_participants_ids():
    with db:
        df = db.query_df("SELECT participant_id FROM raw.participants;")
        return df

def get_all_participants():
    try:
        with db:
            df = db.query_df("SELECT * FROM raw.participants;")
            return df
    except Exception as e:
        db.rollback()
        print(f"Error fetching participants: {e}")
        return None

        
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

    update_values = []

    for classroom_label, student_ids in allocations.items():
        try:
            classroom_id = int(classroom_label.split("_")[1])  # e.g., "Classroom_3" -> 3
        except (IndexError, ValueError):
            return {"error": f"Invalid classroom label: {classroom_label}"}, 400

        for student_id in student_ids:
            try:
                update_values.append((int(student_id), classroom_id))
            except ValueError:
                return {"error": f"Invalid student ID: {student_id}"}, 400

    if not update_values:
        return {"error": "No valid student allocations found"}, 400

    try:
        db.execute_many("""
            INSERT INTO raw.allocations (participant_id, classroom_id)
            VALUES (%s, %s)
            ON CONFLICT (participant_id) DO UPDATE
            SET classroom_id = EXCLUDED.classroom_id;
        """, update_values)

        # You may need this depending on your DB setup
        db.commit()

    except Exception as e:
        db.rollback()
        return {"error": f"Database error: {str(e)}"}, 500

    return {
        "message": "Allocations updated successfully",
        "total_updated": len(update_values)
    }, 200


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


def classroom_update(participant_id: int, classroom_id: str):
    """
    Update the classroom for a given participant_id.
    If the participant_id doesn't exist, insert it.
    Returns a dict with operation status and relevant info.
    """
    print(participant_id)
    print(classroom_id)
    try:
        full_classroom_id = f"Classroom_{classroom_id}"

        db.execute_query("""
            UPDATE public.classroom_allocation
            SET classroom_id = %s
            WHERE participant_id = %s
            RETURNING participant_id;
        """, (full_classroom_id, participant_id))
        
        db.commit()
        return {
            "status": "success",
            "participant_id": participant_id,
            "classroom_id": classroom_id
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback() 
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


def get_allocations_from_db(db, run_number: int) -> dict:
    query = """
    SELECT classroom_id, participant_id
    FROM public.classroom_allocation
    WHERE run_number = %s
    """

    with db:
        results = db.query(query, (run_number,))  # Use db.fetch_all or equivalent if available

    allocations = {}
    for classroom_id, participant_id in results:
        allocations.setdefault(classroom_id, []).append(participant_id)

    return {
        "RunNumber": run_number,
        "Allocations": allocations
    }


def get_latest_allocations_from_db(db_session) -> dict:
    latest_run_result = db_session.fetch_one(
        "SELECT run_number FROM public.classroom_allocation ORDER BY created_at DESC LIMIT 1"
    )

    if not latest_run_result:
        return {
            "RunNumber": None,
            "Allocations": {},
            "Details": {}
        }

    latest_run_number = latest_run_result[0]

    df = db_session.query_df(
        """
        SELECT 
            alloc.classroom_id, 
            alloc.participant_id,
            par.first_name,
            par.last_name
        FROM 
            public.classroom_allocation AS alloc
        LEFT JOIN 
            raw.participants AS par 
            ON alloc.participant_id = par.participant_id
        WHERE 
            alloc.run_number = %s
        """,
        (latest_run_number,)
    )

    allocations = {}
    details_lookup = {}

    for _, row in df.iterrows():
        classroom_id = row['classroom_id']
        participant_id = row['participant_id']
        allocations.setdefault(classroom_id, []).append(participant_id)
        details_lookup[participant_id] = {
            "first_name": row.get("first_name", ""),
            "last_name": row.get("last_name", "")
        }

    return {
        "RunNumber": str(latest_run_number),
        "Allocations": allocations,
        "Details": details_lookup
    }
