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
    db: Database,
    constraint_map: Dict[int, float],
    academic_weight: float = 2.0,
    all_constraints: Dict[str, Dict[int, float]] = None,
) -> dict:

    """
    Evenly allocates students into classrooms while trying to balance average academic score.
    """
    student_ids = data.student_ids
    embeddings = data.embeddings.cpu().numpy()

    # Normalize academic scores
    academic_scores = np.array([constraint_map.get(int(sid), 0) for sid in student_ids])
    min_score, max_score = academic_scores.min(), academic_scores.max()
    norm_scores = (academic_scores - min_score) / (max_score - min_score + 1e-6)

    # Extend embeddings with weighted academic score
    extended_embeddings = np.hstack([
        embeddings,
        (academic_weight * norm_scores[:, np.newaxis])
    ])

    # Get student list with academic info
    student_list = list(zip(student_ids, extended_embeddings, norm_scores))

    # Sort by academic score (descending)
    student_list.sort(key=lambda x: x[2], reverse=True)

    # Initialize balanced bins
    max_per_group = math.ceil(len(student_list) / num_allocations)
    assignments = {i: [] for i in range(num_allocations)}
    group_scores = {i: 0.0 for i in range(num_allocations)}

    # Round-robin assign students to group with lowest total academic score & not full
    for student_id, emb, score in student_list:
        eligible_groups = [
            gid for gid in range(num_allocations)
            if len(assignments[gid]) < max_per_group
        ]
        best_group = min(eligible_groups, key=lambda gid: group_scores[gid])
        assignments[best_group].append(int(student_id))
        group_scores[best_group] += score

    # Logging
    for gid in assignments:
        avg_score = group_scores[gid] / len(assignments[gid])
        logger.info(f"Classroom {gid + 1}: {len(assignments[gid])} students, avg perc_academic = {avg_score:.2f}")

    allocations = {f"{gid + 1}": members for gid, members in assignments.items()}
    avg_performance_scores = {}
    for cluster_id, members in assignments.items():
        scores = [constraint_map.get(sid, 0) for sid in members]
        avg_score = np.mean(scores) if scores else 0
        avg_performance_scores[str(cluster_id + 1)] = avg_score
        print(avg_score)

    # Compute average scores for all metrics per classroom
    average_metrics_per_classroom = {}

    for metric_name, metric_map in (all_constraints or {}).items():
        average_metrics_per_classroom[metric_name] = {}
        for cluster_id, members in assignments.items():
            scores = [metric_map.get(sid, 0) for sid in members]
            avg_score = np.mean(scores) if scores else 0
            average_metrics_per_classroom[metric_name][str(cluster_id + 1)] = avg_score

  # Key matches frontend classroom keys

    result = {
        "Total_Students": len(student_ids),
        "Total_Classrooms": num_allocations,
        "Allocations": allocations,
        "AveragePerformance": average_metrics_per_classroom  # <-- now holds all metrics
    }


    return result

