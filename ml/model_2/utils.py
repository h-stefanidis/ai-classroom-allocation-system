from collections import defaultdict
from flask import jsonify
from ml.model_2.construct_graph import construct_graph
from db.db_manager import get_db

def relationship_counts_per_class():
    """
    Returns the number of each relationship type per classroom for the most recent allocation run.
    Also includes 'isolation': number of students in each classroom without a single friend within that classroom.
    Always includes all relationship types (even if count is zero).
    """

    db = get_db()
    # 1. Get the latest run_number from classroom_allocation (ordered by id)
    run_query = """
        SELECT run_number FROM classroom_allocation
        ORDER BY id DESC
        LIMIT 1
    """
    run_result = db.query_df(run_query)
    if run_result.empty:
        return jsonify({"error": "No allocation runs found"}), 404
    run_number = run_result.iloc[0]["run_number"]

    # 2. Get the mapping of participant_id to classroom_id for this run
    alloc_query = """
        SELECT participant_id, classroom_id
        FROM classroom_allocation
        WHERE run_number = %s
    """
    alloc_df = db.query_df(alloc_query, (run_number,))
    student_to_class = dict(zip(alloc_df["participant_id"], alloc_df["classroom_id"]))

    # 3. Build the graph (or get it from your pipeline)
    graph = construct_graph(db)

    # 4. Prepare relationship type mapping (consistent with construct_graph)
    EDGE_TYPE_MAP =  {
        "friends": 0,
        "influential": 1,
        "feedback": 2,
        "more_time": 3,
        "advice": 4,
        "disrespect": 5
    }

    EDGE_TYPE_LABELS = {v: k for k, v in EDGE_TYPE_MAP.items()}
    REL_TYPES = list(EDGE_TYPE_MAP.keys())

    # 5. Count relationships per class
    class_rel_counts = defaultdict(lambda: defaultdict(int))
    # For isolation: track students in each class and their in-class friends
    class_students = defaultdict(set)
    in_class_friends = defaultdict(lambda: defaultdict(set))  # class_id -> student -> set(friend)

    for u, v, d in graph.edges(data=True):
        rel_type = d.get("edge_type")
        rel_name = EDGE_TYPE_LABELS.get(rel_type, f"rel_{rel_type}")
        class_u = student_to_class.get(u)
        class_v = student_to_class.get(v)
        # Only count if both students are in the same class
        if class_u is not None and class_u == class_v:
            class_rel_counts[class_u][rel_name] += 1
            class_students[class_u].add(u)
            class_students[class_u].add(v)
            # Track friends for isolation
            if rel_type == EDGE_TYPE_MAP['friends']:
                in_class_friends[class_u][u].add(v)
                in_class_friends[class_u][v].add(u)

    # Always include all relationship types, even if zero
    result = {
        "run_number": run_number,
        "relationship_counts": {},
    }

    for class_id, rel_counts in sorted(class_rel_counts.items(), key=lambda x: int(x[0])):
        # Isolation: students with no in-class friends
        students = class_students[class_id]
        friends_map = in_class_friends[class_id]
        isolated_count = sum(1 for s in students if len(friends_map.get(s, set())) == 0)
        result["relationship_counts"][str(class_id)] = {
            **{rel: rel_counts.get(rel, 0) for rel in REL_TYPES},
            "isolation": isolated_count
        }

    print(result)
    return jsonify(result)