from typing import List, Dict
import torch
import logging
import math
from db.database import Database
from sklearn.cluster import KMeans
import numpy as np
from torch_geometric.data import Data

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def allocate_students(
    data: Data,
    num_allocations: int,
    db: Database
) -> dict:
    """
    Allocates students into classrooms using clustering on embeddings stored in `data`.

    Args:
        data (Data): PyG data object with `embeddings` and `student_ids`.
        num_allocations (int): Number of classrooms.
        db (Database): Database connection.

    Returns:
        dict: Allocation results in the format:
        {
            "Total_Students": int,
            "Total_Classrooms": int,
            "Allocations": {"Classroom_1": [...], ...}
        }
    """
    embeddings = data.embeddings
    student_ids = data.student_ids
    num_students = embeddings.size(0)

    logger.info(f"Allocating {num_students} students into {num_allocations} balanced groups.")
    kmeans = KMeans(n_clusters=num_allocations, random_state=42)
    kmeans.fit(embeddings.cpu().numpy())
    centers = kmeans.cluster_centers_

    assignments = {i: [] for i in range(num_allocations)}
    max_size = math.ceil(num_students / num_allocations)

    distances = []
    for idx, emb in enumerate(embeddings.cpu().numpy()):
        dists = [np.linalg.norm(emb - center) for center in centers]
        distances.append((idx, dists))

    distances.sort(key=lambda x: min(x[1]))

    for idx, dists in distances:
        sorted_clusters = sorted(enumerate(dists), key=lambda x: x[1])
        for cluster_id, _ in sorted_clusters:
            if len(assignments[cluster_id]) < max_size:
                assignments[cluster_id].append(int(student_ids[idx]))  # Ensure Python int
                break

    # Format output as {"Classroom_1": [...], "Classroom_2": [...], ...}
    allocations = {f"Classroom_{cluster_id + 1}": student_list for cluster_id, student_list in assignments.items()}

    result = {
        "Total_Students": num_students,
        "Total_Classrooms": num_allocations,
        "Allocations": allocations
    }

    for classroom, students in allocations.items():
        logger.info(f"{classroom} → {len(students)} students")
    return result