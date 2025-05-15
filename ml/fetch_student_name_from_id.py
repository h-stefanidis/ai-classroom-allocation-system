from flask import Blueprint, request, jsonify
import uuid
from db.db_usage import save_allocations_to_db

def generate_run_number():
    return str(uuid.uuid4()) 

def fetch_student_name_from_id(db, json_data):
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

