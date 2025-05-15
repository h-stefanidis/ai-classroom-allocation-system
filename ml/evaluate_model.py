import torch
from collections import defaultdict
import pandas as pd
 
 
 
def load_participant_data(db):
    participants_query = """
        SELECT participant_id, first_name, last_name, perc_academic
        FROM raw.participants
        WHERE participant_id IS NOT NULL
    """
    participants_df = db.query_df(participants_query)
 
    if participants_df.empty:
        raise ValueError("No participants found in the database.")
 
    # Coerce perc_academic to numeric (converts 'NA' to NaN)
    participants_df["perc_academic"] = pd.to_numeric(participants_df["perc_academic"], errors="coerce")
 
    # Always include all participant IDs (in graph)
    participant_ids = participants_df["participant_id"].tolist()
 
    # Build dictionaries
    id_to_name = {
        int(row["participant_id"]): f"{row['first_name']} {row['last_name']}"
        for _, row in participants_df.iterrows()
    }
 
    academic_scores = {
        int(row["participant_id"]): float(row["perc_academic"])
        for _, row in participants_df.iterrows()
        if not pd.isna(row["perc_academic"])
    }
 
    return participant_ids, id_to_name, academic_scores
 
 
 
 
def evaluate_relationships(data, cluster_labels, participant_ids, id_to_name, academic_scores):
    EDGE_TYPE = {
        0: "friend",
        1: "influence",
        2: "feedback",
        3: "more_time",
        4: "advice",
        5: "disrespect"
    }
 
    preserved_counts = defaultdict(int)
    total_counts = defaultdict(int)
    classroom_edge_counts = defaultdict(lambda: defaultdict(int))
    disrespect_violations = defaultdict(list)
    disrespect_counts = defaultdict(int)
    friends_per_node = defaultdict(set)
    influence_targets = defaultdict(set)
    cluster_members = defaultdict(list)
 
    # Analyze edges
    for idx in range(data.edge_index.shape[1]):
        src, tgt = data.edge_index[:, idx]
        rel = int(data.edge_type[idx])
        rel_name = EDGE_TYPE[rel]
        src_class = cluster_labels[src]
        tgt_class = cluster_labels[tgt]
 
        total_counts[rel_name] += 1
        if src_class == tgt_class:
            preserved_counts[rel_name] += 1
            classroom_edge_counts[src_class][rel_name] += 1
 
            if rel == 5:  # Disrespect
                src_pid = participant_ids[src]
                tgt_pid = participant_ids[tgt]
                disrespect_violations[src_class].append((src_pid, tgt_pid))
                disrespect_counts[src_class] += 1
 
        # Track friends and influence
        if rel == 0:
            friends_per_node[src].add(tgt)
            friends_per_node[tgt].add(src)
        if rel == 1:
            influence_targets[src].add(tgt)
 
    # Assign participants to clusters
    for i, label in enumerate(cluster_labels):
        cluster_members[label].append(participant_ids[i])
 
    # Academic mean per class
    academic_distribution = {}
    for cls, members in cluster_members.items():
        scores = [academic_scores[pid] for pid in members if pid in academic_scores]
        if scores:
            academic_distribution[cls] = {
                "mean": sum(scores) / len(scores),
                "count": len(scores),
                "min": min(scores),
                "max": max(scores)
            }
        else:
            academic_distribution[cls] = {
                "mean": None, "count": 0, "min": None, "max": None
            }
 
    # Isolation count
    all_nodes = set(range(len(participant_ids)))
    isolated_nodes = [i for i in all_nodes if i not in friends_per_node]
    isolation_count = len(isolated_nodes)
 
    # Influence spread
    influence_spread = {
        participant_ids[src]: len(targets)
        for src, targets in influence_targets.items()
    }
 
    metrics = {
        "relationship_preservation": {
            rel_name: {
                "preserved": preserved_counts.get(rel_name, 0),
                "total": total_counts.get(rel_name, 0),
                "percentage": (100 * preserved_counts.get(rel_name, 0) / total_counts.get(rel_name, 0))
                if total_counts.get(rel_name, 0) > 0 else 0
            }
            for rel_name in EDGE_TYPE.values()
        },
        "classroom_relationships": {
            cls: {
                rel_name: classroom_edge_counts[cls].get(rel_name, 0)
                for rel_name in EDGE_TYPE.values()
            }
            for cls in sorted(classroom_edge_counts.keys())
        },
        "disrespect_violations": {
            cls: [
                {"source_id": src_pid, "target_id": tgt_pid,
                 "source_name": id_to_name.get(src_pid, "Unknown"),
                 "target_name": id_to_name.get(tgt_pid, "Unknown")}
                for src_pid, tgt_pid in disrespect_violations[cls]
            ]
            for cls in disrespect_violations
        },
        "disrespect_counts_per_class": dict(disrespect_counts),
        "academic_distribution_per_class": academic_distribution,
        "isolation_count": isolation_count,
        "friend_counts": {
            participant_ids[i]: len(friends_per_node[i])
            for i in friends_per_node
        },
        "influence_spread": influence_spread,
        "group_sizes": {
            cls: len(members)
            for cls, members in cluster_members.items()
        }
    }
 
    return metrics
 
 
def evaluate_model(data, db):
    """
    Main function to evaluate the model.
 
    Args:
        data (torch_geometric.data.Data): The graph data.
        db: Database connection object.
 
    Returns:
        dict: Metrics as a JSON-like dictionary.
    """
    if not hasattr(data, "y"):
        raise ValueError("No cluster labels found in the graph.")
 
    cluster_labels = data.y.tolist()
    participant_ids, id_to_name, academic_scores = load_participant_data(db)
    metrics = evaluate_relationships(data, cluster_labels, participant_ids, id_to_name, academic_scores)
    return metrics
 
 