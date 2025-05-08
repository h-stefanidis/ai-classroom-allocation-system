import torch
import pandas as pd
import json
from collections import defaultdict
import os



def export_clusters(participants_df, pt_path="data/student_graph_clustered.pt", output_dir="ml/data"):
    # Load clustered graph
    data = torch.load(pt_path, weights_only=False)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Validate input DataFrame
    if "Participant-ID" not in participants_df.columns:
        raise ValueError("Input DataFrame must contain a 'Participant-ID' column.")

    participant_ids = participants_df["Participant-ID"].astype(int).tolist()
    cluster_labels = data.y.tolist()

    if len(participant_ids) != len(cluster_labels):
        raise ValueError("Mismatch between number of participant IDs and number of cluster labels.")

    num_students = len(participant_ids)
    num_classrooms = len(set(cluster_labels))

    # -----------------------------
    # Save flat CSV allocation
    # -----------------------------
    csv_df = pd.DataFrame({
        "Participant-ID": participant_ids,
        "Classroom": cluster_labels
    })

    csv_path = os.path.join(output_dir, "classroom_allocations.csv")
    csv_df.to_csv(csv_path, index=False)
    print(f"CSV allocation list saved to: {csv_path}")

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

    json_path = os.path.join(output_dir, "classroom_allocations.json")
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2)

    print(f"JSON allocation (grouped) saved to: {json_path}")
    print(f"Total Students: {num_students}")
    print(f"Total Classrooms: {num_classrooms}")
