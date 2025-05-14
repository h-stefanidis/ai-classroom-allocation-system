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
) -> List[Dict]:
    """
    Allocates students into classrooms using clustering on embeddings stored in `data`.

    Args:
        data (Data): PyG data object with `embeddings` and `student_ids`.
        num_allocations (int): Number of classrooms.
        db (Database): Database connection.

    Returns:
        List[Dict]: Allocation results.
    """
    embeddings = data.embeddings
    student_ids = data.student_ids
    num_students = embeddings.size(0)

    logger.info(f"Allocating {num_students} students into {num_allocations} balanced groups.")
    ##todo: Different approach to clustering add if statements to this.
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
                assignments[cluster_id].append(student_ids[idx])
                break

    data_to_insert = [(cluster_id, student_id) for cluster_id, student_list in assignments.items() for student_id in student_list]

    insert_query = """
        INSERT INTO allocation_students (allocation_id, student_id)
        VALUES (%s, %s)
    """

    try:
        db.execute_many(insert_query, data_to_insert)
        logger.info(f"Inserted {len(data_to_insert)} student allocations into the database.")
    except Exception as e:
        logger.error(f"Failed to insert allocations: {e}")

    result = [{"allocation_id": cluster_id, "students": student_list}
              for cluster_id, student_list in assignments.items()]

    for r in result:
        logger.info(f"Class {r['allocation_id']} → {len(r['students'])} students")
    return result
