import torch
import pandas as pd
from collections import defaultdict
from pathlib import Path

def analyze_graph(participants_df: pd.DataFrame):

    graph_path = Path(__file__).resolve().parent.parent / "data" / "student_graph.pt"
    data = torch.load(graph_path, weights_only=False)



    if not hasattr(data, "y"):
        raise ValueError("No cluster labels found in the graph.")

    cluster_labels = data.y.tolist()

    # === Use participant_ids from data if available, else fallback to participants_df ===
    if hasattr(data, "participant_ids"):
        participant_ids = data.participant_ids.tolist()
    else:
        participant_ids = participants_df["participant_id"].tolist()

    # === Build ID to Name mapping from the provided DataFrame ===
    if "first_name" in participants_df.columns and "last_name" in participants_df.columns:
        id_to_name = {
            int(row["participant_id"]): f"{row['first_name']} {row['last_name']}"
            for _, row in participants_df.iterrows()
        }
    else:
        id_to_name = {}

    # === Relationship Types ===
    EDGE_TYPE = {
        0: "friend",
        1: "influence",
        2: "feedback",
        3: "more_time",
        4: "advice",
        5: "disrespect"
    }

    # === Global preservation stats ===
    preserved_counts = defaultdict(int)
    total_counts = defaultdict(int)

    # === Per-classroom edge counters and disrespect pairs ===
    classroom_edge_counts = defaultdict(lambda: defaultdict(int))
    disrespect_violations = defaultdict(list)

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

    # === Global Summary Report ===
    print("Relationship Preservation Report:\n")
    for rel_name in EDGE_TYPE.values():
        preserved = preserved_counts.get(rel_name, 0)
        total = total_counts.get(rel_name, 0)
        percent = (100 * preserved / total) if total > 0 else 0
        status = "Preserved" if rel_name != "disrespect" else "Violated"
        print(f"- {rel_name.capitalize():<12} {status:<10}: {preserved} / {total}  ({percent:.2f}%)")

    # === Per-Classroom Breakdown ===
    print("\nPer-Classroom Relationship Summary (with disrespect details):\n")
    for cls in sorted(classroom_edge_counts.keys()):
        print(f"Classroom {cls}:")
        for rel_name in EDGE_TYPE.values():
            count = classroom_edge_counts[cls].get(rel_name, 0)
            print(f"  - {rel_name:<12}: {count}")

        # Inline list of disrespect pairs (with names)
        if cls in disrespect_violations:
            for src_pid, tgt_pid in disrespect_violations[cls]:
                src_name = id_to_name.get(src_pid, "Unknown")
                tgt_name = id_to_name.get(tgt_pid, "Unknown")
                print(f"    ➡️ {src_pid} ({src_name}) X {tgt_pid} ({tgt_name})")
        print()
