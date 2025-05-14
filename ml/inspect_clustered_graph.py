import torch
import pandas as pd
from collections import defaultdict

# Load the clustered graph
data = torch.load("data/student_graph_clustered.pt")

# Load participant IDs (from graph or Excel)
if hasattr(data, "participant_ids"):
    participant_ids = data.participant_ids.tolist()
else:
    # Fallback: Load from Excel
    participants = pd.read_excel("SchoolData/Student Survey - Jan.xlsx", sheet_name="participants")
    participants = participants.dropna(subset=["Participant-ID"]).reset_index(drop=True)
    participant_ids = participants["Participant-ID"].astype(int).tolist()

# Cluster assignments
cluster_labels = data.y.tolist()

# Count and group students by cluster
clusters = defaultdict(list)
for i, label in enumerate(cluster_labels):
    clusters[label].append(participant_ids[i])

# Summary
print(f"👥 Total Students: {len(participant_ids)}")
print(f"🏫 Total Classrooms (Clusters): {len(set(cluster_labels))}\n")

# Print students per cluster
for cluster_id, student_ids in clusters.items():
    print(f"📘 Classroom {cluster_id} — {len(student_ids)} students")
    print("Participant-IDs:", student_ids)
    print("-" * 60)
