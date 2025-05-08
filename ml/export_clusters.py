import torch
import pandas as pd
from collections import defaultdict
import json

# Load clustered graph
data = torch.load("data/student_graph_clustered.pt")

# Load Participant-IDs
if hasattr(data, "participant_ids"):
    participant_ids = data.participant_ids.tolist()
else:
    participants = pd.read_excel("SchoolData/Student Survey - Jan.xlsx", sheet_name="participants")
    participants = participants.dropna(subset=["Participant-ID"]).reset_index(drop=True)
    participant_ids = participants["Participant-ID"].astype(int).tolist()

# Cluster labels
cluster_labels = data.y.tolist()

# Basic counts
num_students = len(participant_ids)
num_classrooms = len(set(cluster_labels))

# -----------------------------
# Save flat CSV allocation
# -----------------------------
csv_df = pd.DataFrame({
    "Participant-ID": participant_ids,
    "Classroom": cluster_labels
})

csv_path = "data/classroom_allocations.csv"
csv_df.to_csv(csv_path, index=False)
print(f"✅ CSV allocation list saved to: {csv_path}")

# -----------------------------
# Save grouped JSON allocation
# -----------------------------
allocations_by_class = defaultdict(list)
for pid, label in zip(participant_ids, cluster_labels):
    allocations_by_class[f"Classroom_{label}"].append(pid)

json_data = {
    "Total_Students": num_students,
    "Total_Classrooms": num_classrooms,
    "Allocations": allocations_by_class
}

json_path = "data/classroom_allocations.json"
with open(json_path, "w") as f:
    json.dump(json_data, f, indent=2)

print(f"✅ JSON allocation (grouped) saved to: {json_path}")
print(f"👥 Total Students: {num_students}")
print(f"🏫 Total Classrooms: {num_classrooms}")
