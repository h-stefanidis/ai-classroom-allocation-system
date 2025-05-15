import random
from collections import defaultdict

def random_classroom_allocator(num_allocations, db, cohort=None):
    """
    Randomly assigns students to classrooms, optionally filtering by cohort.

    Args:
        num_allocations (int): Number of classrooms.
        db: Database connection (expects a method to fetch all participant IDs).
        cohort (int or str, optional): Cohort year to filter students.

    Returns:
        dict: Allocation results in the format:
        {
            "Total_Students": int,
            "Total_Classrooms": int,
            "Allocations": defaultdict(list)
        }
    """
    # Fetch all participant IDs from the database, optionally filtering by cohort
    query = "SELECT participant_id FROM raw.participants"
    if cohort is not None:
        query += f" WHERE cohort = '{cohort}'"
    with db:
        result = db.query_df(query)
        student_ids = result["participant_id"].tolist()

    random.shuffle(student_ids)

    allocations = defaultdict(list)
    for idx, student_id in enumerate(student_ids):
        classroom = f"Classroom_{(idx % num_allocations) + 1}"
        allocations[classroom].append(student_id)

    return {
        "Total_Students": len(student_ids),
        "Total_Classrooms": num_allocations,
        "Allocations": allocations
    }