from typing import List, Dict
import torch
import logging
from db.database import Database
from sklearn_extra.cluster import KMeansConstrained
import math

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def allocate_students(
    embeddings: torch.Tensor,
    num_allocations: int,
    db: Database
) -> List[Dict]:
    """
    Allocates students into classrooms using size-constrained KMeans clustering
    on GNN embeddings and inserts the results into the `allocation_students` table.

    Args:
        embeddings (torch.Tensor): Node embeddings [num_nodes, embedding_dim].
        num_allocations (int): Number of clusters (classrooms).
        db (Database): Database connection object.

    Returns:
        List[Dict]: Allocation results in JSON-like format.
    """
    num_students = embeddings.size(0)
    node_ids = list(range(num_students))

    # Calculate size constraints
    min_size = math.floor(num_students / num_allocations)
    max_size = math.ceil(num_students / num_allocations)

    logger.info(f"Allocating {num_students} students into {num_allocations} balanced clusters.")
    logger.info(f"Min cluster size: {min_size}, Max cluster size: {max_size}")

    # Perform constrained KMeans clustering
    kmeans = KMeansConstrained(
        n_clusters=num_allocations,
        size_min=min_size,
        size_max=max_size,
        random_state=42
    )
    cluster_labels = kmeans.fit_predict(embeddings.cpu().numpy())

    # Group students by cluster
    allocations = [{"allocation_id": i, "students": []} for i in range(num_allocations)]
    for node_id, cluster_id in zip(node_ids, cluster_labels):
        allocations[cluster_id]["students"].append(node_id)

    # Insert allocations into the database
    insert_query = """
        INSERT INTO allocation_students (allocation_id, student_id)
        VALUES (%s, %s)
    """
    data_to_insert = [(cluster_id, student_id) for cluster_id, student_id in zip(cluster_labels, node_ids)]
    try:
        db.execute_many(insert_query, data_to_insert)
        logger.info(f"Inserted {len(data_to_insert)} student allocations into the database.")
    except Exception as e:
        logger.error(f"Failed to insert student allocations: {e}")

    # Log cluster sizes
    for allocation in allocations:
        logger.info(f"Cluster {allocation['allocation_id']} has {len(allocation['students'])} students.")

    return allocations
