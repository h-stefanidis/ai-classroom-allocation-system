import pandas as pd
from collections import defaultdict

def export_clusters(clustered_data):
    """
    Exports classroom allocations from clustered data.
    
    Args:
        clustered_data (torch_geometric.data.Data): Clustered graph data with participant IDs and cluster labels.
    
    Returns:
        dict: JSON object containing student allocations.
    """
    # Load Participant-IDs
    if hasattr(clustered_data, "participant_ids"):
        participant_ids = clustered_data.participant_ids.tolist()
    else:
        raise ValueError("Participant IDs are missing in the clustered data.")

    # Cluster labels
    cluster_labels = clustered_data.y.tolist()

    # Basic counts
    num_students = len(participant_ids)
    num_classrooms = len(set(cluster_labels))

    # Create grouped JSON allocation
    allocations_by_class = defaultdict(list)
    for pid, label in zip(participant_ids, cluster_labels):
        allocations_by_class[f"Classroom_{label}"].append(pid)

    json_data = {
        "Total_Students": num_students,
        "Total_Classrooms": num_classrooms,
        "Allocations": allocations_by_class
    }

    return json_data