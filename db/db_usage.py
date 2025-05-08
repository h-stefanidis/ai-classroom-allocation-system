import sys
from pathlib import Path
import hashlib

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from db_manager import get_db
from ml.build_graph import build_graph_from_dataframe
from ml.export_clusters import export_clusters
from ml.cluster_with_gnn_with_constraints import cluster_constraints
from ml.evaluate_model import analyze_graph
#import ml.evaluate_model
import json
from pathlib import Path

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


def classroom_allocation():
    # Step 1: Load participant dataframe (if needed elsewhere)

    participants_df = get_all_participants()

    feature_columns = ["participant_id", "perc_effort", "attendance", "perc_academic", "complete_years", "house"]
    filtered_df = participants_df[feature_columns + ["participant_id"]]

    print(participants_df)

    build_graph_from_dataframe(filtered_df)
    allocation_data = export_clusters(participants_df)


    ## Step 2: Load JSON file
    #json_path = Path("ml/classforge_project/SchoolData/data/classroom_allocations.json")
    #with open(json_path, "r") as f:
    #    allocation_data = json.load(f)

    allocations = allocation_data["Allocations"]

    # Step 3: Clear old allocations (optional, depending on your use case)
    db.execute("DELETE FROM raw.allocations")

    # Step 3.5: Update allocations table with new allocations
    cluster_constraints()
    export_clusters()

    for classroom_label, student_ids in allocations.items():
    classroom_id = int(classroom_label.split("_")[1])  # e.g., "Classroom_2" -> 2
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
            insert_values.append((student_id, classroom_number))

    # Step 5: Perform batch insert
    db.execute_many(
        table="raw.allocations",
        columns=["student_id", "classroom"],
        values=insert_values
    )

    return {"message": "Allocations updated", "total": len(insert_values)}


# For login and sign up
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()



def register_user(email, password, username, role="user"):
    password_hash = hash_password(password)

    with db:
        query = """
        INSERT INTO public.users (email, password_hash,username, role)
        VALUES (%s, %s, %s)
        ON CONFLICT (email) DO NOTHING;
        """
        db.execute_query(query, (email, password_hash,username, role))



def login_user(email, password):
    password_hash = hash_password(password)

    with db:
        query = """
        SELECT user_id, role FROM public.users
        WHERE email = %s AND password_hash = %s;
        """
        result = db.query_one(query, (email, password_hash))

    if result:
        return {"user_id": result[0], "role": result[1]}
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

    

def inspect_clustered_graph():
    participants_df = get_all_participants()

   

# TODO: Move out of file?
#create_allocations_table() # Works
#populate_allocations_table() # Maybe works, maybe duplicates TODO: Fix and reassure
#classroom_allocation_update()

# Build Graph From DataFrame 
#alldf = get_all_participants()

#friends_df = get_all_friends()
#influential_df = get_all_influential()
#feedback_df = get_all_feedback()
#more_time_df = get_all_more_time()
#advice_df = get_all_advice()
#disrespect_df = get_all_disrespect()

#build_graph_from_dataframe(alldf, friends_df, influential_df, feedback_df, more_time_df, advice_df, disrespect_df)

# Cluster Constraints
#cluster_constraints()


#Analyze graph
#alldf = get_all_participants()
#analyze_graph(alldf)



## Export Clusters
#export_clusters()
