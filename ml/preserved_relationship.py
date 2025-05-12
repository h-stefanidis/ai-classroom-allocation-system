from collections import defaultdict

def compute_preserved_relationships(db, clustered_data, run_number):
    relation_counts_per_group = defaultdict(lambda: defaultdict(int))
    EDGE_TYPE = {
        0: "friend",
        1: "influence",
        2: "feedback",
        3: "more_time",
        4: "advice",
        5: "disrespect"
    }

    edge_index = clustered_data.edge_index
    edge_type = clustered_data.edge_type
    cluster_labels = clustered_data.y

    for i in range(edge_index.shape[1]):
        src = edge_index[0, i].item()
        dst = edge_index[1, i].item()
        rel_type = edge_type[i].item()

        group_src = cluster_labels[src].item()
        group_dst = cluster_labels[dst].item()

        if group_src == group_dst:
            relation_name = EDGE_TYPE.get(rel_type, f"rel_{rel_type}")
            relation_counts_per_group[group_src][relation_name] += 1

    # Convert to DataFrame for easier analysis
    import pandas as pd
    group_summary = []
    for group_id, relations in relation_counts_per_group.items():
        row = {"Group ID": group_id}
        row.update(relations)
        group_summary.append(row)

    realtionship_df = pd.DataFrame(group_summary).fillna(0).astype({"Group ID": int}).sort_values("Group ID")
    save_relationship_db(db, realtionship_df, run_number)

def save_relationship_db(db, df, run_number):
    # Normalize column names
    print(df)
    df.columns = df.columns.str.strip().str.lower()

    # Rename group id and drop 'id' if present
    df = df.rename(columns={"group id": "group_id"}).fillna(0).astype(int)
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    # Add run number
    df["group_id"] = df["group_id"].astype(str)
    df["run_number"] = run_number
    print("DataFrame columns before insert:----------", df.columns.tolist())

    # Prepare and insert
    columns = list(df.columns)
    data = [tuple(row) for row in df.to_numpy()]
    placeholders = ", ".join(["%s"] * len(columns))
    col_str = ", ".join(columns)

    query = f"""
        INSERT INTO public.preserve_edge ({col_str})
        VALUES ({placeholders})
    """

    with db:
        db.execute_many(query, data)

    print(f"Saved {len(data)} group-level relationship rows for run {run_number}")
