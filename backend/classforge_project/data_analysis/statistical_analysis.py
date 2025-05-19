import pandas as pd
from collections import defaultdict
from db.db_manager import get_db


def normalize_psychometric_scores(responses_df, psychometric_columns):
    # Normalize each column to 0-1 scale using min-max normalization
    norm_df = responses_df.copy()
    for col in psychometric_columns:
        min_val = responses_df[col].min()
        max_val = responses_df[col].max()
        if pd.notnull(min_val) and pd.notnull(max_val) and max_val != min_val:
            norm_df[col] = (responses_df[col] - min_val) / (max_val - min_val)
        else:
            norm_df[col] = 0.0  # if all values are the same or null, set to 0
    return norm_df


def final_calculate_with_normalized_scores(run_number, cohort="2025"):
    print("---------", run_number)
    db= get_db()


    # Step 0: Get latest run_number if not provided
    latest_df = db.query_df("""
        SELECT run_number
        FROM public.classroom_allocation
        ORDER BY id DESC
        LIMIT 1
    """)
    if not run_number:
        if latest_df.empty:
            return {"error": "No run_number found."}
        run_number = latest_df.iloc[0]["run_number"]

    print("---------", run_number, cohort)

    # Step 1: Get cohort participants
    participants_df = db.query_df("SELECT participant_id FROM raw.participants WHERE cohort = %s", (cohort,))
    print("---------", "after this", participants_df)

    participant_ids = set(participants_df["participant_id"].tolist())

    # Step 2: Get classroom allocations
    alloc_df = db.query_df("""
        SELECT participant_id, classroom_id
        FROM public.classroom_allocation
        WHERE run_number = %s
    """, (run_number,))
    alloc_df = alloc_df[alloc_df["participant_id"].isin(participant_ids)]
    alloc_df["classroom_id"] = alloc_df["classroom_id"].astype(str).str.extract(r"(\d+)").astype(int)
    classroom_map = alloc_df.groupby("classroom_id")["participant_id"].apply(set).to_dict()

    # Step 3: Relationship preservation
    relationship_tables = {
        "friend": "friends", "influence": "influential", "feedback": "feedback",
        "more_time": "more_time", "advice": "advice", "disrespect": "disrespect"
    }
    print("---------", run_number)

    preservation_result = {}
    for rel_type, table in relationship_tables.items():
        raw_edges_df = db.query_df(f"""
            SELECT source, target FROM raw.{table}
            WHERE source IN %s AND target IN %s
        """, (tuple(participant_ids), tuple(participant_ids)))
        total_original = raw_edges_df.shape[0]

        preserved_df = db.query_df("""
            SELECT source_id, target_id, classroom_id
            FROM public.edge_relationship
            WHERE run_number = %s AND relationship_type = %s
        """, (run_number, rel_type))
        preserved_df["classroom_id"] = preserved_df["classroom_id"].astype(int)

        preservation_result[rel_type] = []
        for classroom_id, class_students in classroom_map.items():
            preserved_count = preserved_df[
                preserved_df["classroom_id"] == classroom_id
            ].shape[0]
            percentage = (preserved_count / total_original * 100) if total_original > 0 else 0.0
            preservation_result[rel_type].append({
                "classroom_id": classroom_id,
                "original": total_original,
                "preserved": preserved_count,
                "percentage": round(percentage, 2)
            })

    # Step 4: Psychometric scores
    responses_df = db.query_df("""
        SELECT r.*, ca.classroom_id
        FROM raw.responses r
        JOIN public.classroom_allocation ca ON r.participant_id = ca.participant_id
        WHERE ca.run_number = %s
    """, (run_number,))
    responses_df = responses_df[responses_df["participant_id"].isin(participant_ids)]
    responses_df["classroom_id"] = responses_df["classroom_id"].astype(str).str.extract(r"(\d+)").astype(int)

    psychometric_columns = [
        "isolated", "women_different", "manbox5_overall", "masculinity_contrained",
        "growth_mindset", "covid", "criticises", "men_better_stem",
        "school_support_engage6", "pwi_wellbeing", "intelligence1", "intelligence2",
        "soft", "opinion", "nerds", "school_support_engage",
        "comfortable", "future", "bullying", "candidate_perc_effort"
    ]

    for col in psychometric_columns:
        responses_df[col] = pd.to_numeric(responses_df[col], errors="coerce")

    classroom_means = (
        responses_df
        .groupby("classroom_id")[psychometric_columns]
        .mean()
        .round(2)
        .reset_index()
    )

    normalized_df = normalize_psychometric_scores(classroom_means, psychometric_columns)

    return {
        "relationship_preservation": preservation_result,
        "psychometrics_by_classroom_normalized": normalized_df.to_dict(orient="records"),
    }
