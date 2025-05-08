import torch
import pandas as pd
from collections import defaultdict

# === Load the clustered graph ===
data = torch.load("data/student_graph_clustered.pt")

if not hasattr(data, "y"):
    raise ValueError("No cluster labels found in the graph.")

cluster_labels = data.y.tolist()

# === Load Participant IDs ===
if hasattr(data, "participant_ids"):
    participant_ids = data.participant_ids.tolist()
else:
    participants_df = pd.read_excel("SchoolData/Student Survey - Jan.xlsx", sheet_name="participants")
    participants_df = participants_df.dropna(subset=["Participant-ID"]).reset_index(drop=True)
    participants_df["Participant-ID"] = participants_df["Participant-ID"].astype(int)
    participant_ids = participants_df["Participant-ID"].tolist()

# === Build ID to Name mapping ===
try:
    id_to_name = {
        int(row["Participant-ID"]): f"{row['First-Name']} {row['Last-Name']}"
        for _, row in participants_df.iterrows()
    }
except:
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
print("📊 Relationship Preservation Report:\n")
for rel_name in EDGE_TYPE.values():
    preserved = preserved_counts.get(rel_name, 0)
    total = total_counts.get(rel_name, 0)
    percent = (100 * preserved / total) if total > 0 else 0
    status = "Preserved" if rel_name != "disrespect" else "Violated"
    print(f"- {rel_name.capitalize():<12} {status:<10}: {preserved} / {total}  ({percent:.2f}%)")

# === Per-Classroom Breakdown ===
print("\n🏫 Per-Classroom Relationship Summary (with disrespect details):\n")
for cls in sorted(classroom_edge_counts.keys()):
    print(f"Classroom {cls}:")
    for rel_name in EDGE_TYPE.values():
        count = classroom_edge_counts[cls].get(rel_name, 0)
        flag = "⚠️" if rel_name == "disrespect" and count > 0 else ""
        print(f"  - {rel_name:<12}: {count} {flag}")

    # Inline list of disrespect pairs (with names)
    if cls in disrespect_violations:
        for src_pid, tgt_pid in disrespect_violations[cls]:
            src_name = id_to_name.get(src_pid, "Unknown")
            tgt_name = id_to_name.get(tgt_pid, "Unknown")
            print(f"    ➡️ {src_pid} ({src_name}) ❌ {tgt_pid} ({tgt_name})")
    print()


