from flask import Blueprint, request, jsonify
import uuid

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
