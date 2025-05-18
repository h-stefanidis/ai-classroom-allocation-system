from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import uuid
import torch

# Database and ML imports
from db.db_manager import get_db
from db.db_usage import (
    get_academic_constraint,
    get_attendance_constraint,
    get_effort_constraint,
    get_latest_allocations_from_db,
    update_classroom_allocations,
    drop_allocations_table,
    create_allocations_table,
    populate_allocations_table,
    save_allocations_to_db,
    generate_run_number,
    fetch_student_dict_from_id,
    get_academic_constraint,
    classroom_update
)

# ML pipeline imports
from ml.build_graph_from_db import build_graph_from_db
from ml.cluster_with_gnn_with_constraints import cluster_students_with_gnn, cluster_students_with_gnn_with_user_input
from ml.export_clusters import export_clusters
from ml.fetch_student_name_from_id import fetch_student_name_from_id
from ml.preserved_relationship import compute_preserved_relationships, save_edge_relationships_db

# Model 2 imports
from ml.model_2.construct_graph import construct_graph
from ml.model_2.graph_conversion import preprocessing
from ml.model_2.model2 import generate_embeddings
from ml.model_2.allocation import allocate_students
from ml.model_2.convert_data_into_graph_cluster import convert_data_in_graph_cluster
from ml.model_2.random_allocator import random_classroom_allocator
from ml.model_2.graph_splitting import attach_names_to_graph, get_split_graphs

pipeline_bp = Blueprint("pipeline", __name__)
main_bp = Blueprint("main_bp", __name__)

@pipeline_bp.route("/get_allocation", methods=['GET'])
def run_samsun_model_pipeline():
    db = get_db()
    classroom_count = int(request.args.get('classroom_count', 4))
    graph = build_graph_from_db(db, 2025)
    participant_ids = [pid.item() if isinstance(pid, torch.Tensor) else pid for pid in graph.participant_ids]
    clustered_data, graph = cluster_students_with_gnn(graph, classroom_count)
    json_data = export_clusters(clustered_data)
    full_json_dict = fetch_student_dict_from_id(db, json_data)
    compute_preserved_relationships(db, clustered_data, full_json_dict["Run_Number"])
    save_edge_relationships_db(db, clustered_data, full_json_dict["Run_Number"], participant_ids)
    return jsonify(full_json_dict)

@pipeline_bp.route("/get_allocation_by_user_preference", methods=['POST'])
@cross_origin(origin='http://localhost:3000')
def get_allocation_by_user_preference_model1():
    db = get_db()
    classroom_count = int(request.args.get('classroom_count', 4))
    cohort = int(request.args.get("cohort", 2025))
    data = request.get_json() or {}
    relationship_weights = data.get("relationship_weights", {})
    graph = build_graph_from_db(db, cohort)
    participant_ids = [pid.item() if isinstance(pid, torch.Tensor) else pid for pid in graph.participant_ids]
    clustered_data, graph = cluster_students_with_gnn_with_user_input(graph, classroom_count, relationship_weights)
    json_data = export_clusters(clustered_data)
    full_json_dict = fetch_student_dict_from_id(db, json_data)
    compute_preserved_relationships(db, clustered_data, full_json_dict["Run_Number"])
    save_edge_relationships_db(db, clustered_data, full_json_dict["Run_Number"], participant_ids)
    return jsonify(full_json_dict)

@pipeline_bp.route("/cytoscape_subgraphs", methods=['GET'])
@cross_origin(origin='http://localhost:3000')
def cytoscape_subgraphs():
    db = get_db()
    graph = construct_graph(db)
    allocations = get_latest_allocations_from_db(db)
    data = get_split_graphs(graph, allocations)
    return jsonify(data)

@pipeline_bp.route('/update_allocations', methods=['POST', 'OPTIONS'])
@cross_origin(origins='http://localhost:3000', methods=['POST', 'OPTIONS'])
def update_classroom_allocations():
    try:
        allocation_json = request.get_json()
        allocations = allocation_json.get("Allocations", {})
        if not allocations:
            return jsonify({"error": "No allocations found in JSON"}), 400

        update_values = []
        for classroom_label, student_ids in allocations.items():
            try:
                classroom_id = int(classroom_label)  # e.g., "Classroom_3" -> 3
            except (IndexError, ValueError):
                return jsonify({"error": f"Invalid classroom format: {classroom_label}"}), 400

            for student_id in student_ids:
                update_values.append((student_id, classroom_id))
                result = classroom_update(student_id, classroom_id)
                if result["status"] != "success":
                    return jsonify({"error": result.get("error", "Update failed")}), 500

        return jsonify({
            "message": "Allocations updated successfully",
            "total_updated": len(update_values)
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@pipeline_bp.route("/run_model2", methods=['GET'])
def run_model2_route():
    """
    Run the Model 2 pipeline: construct graph, convert to PyG, run GNN, allocate students.
    Expects query parameters:
      - 'classroomCount' (int): number of classrooms
      - 'cohort' (int or str): student cohort
      - 'option' (str): which constraint to weight ('perc_academic', 'perc_effort', or 'perc_attendance')
    """
    # Get query parameters
    num_allocations = int(request.args.get('classroomCount', 4))  # default to 4
    cohort = request.args.get('cohort', 2025)                     # default to 2025
    option = request.args.get('option', 'perc_academic')          # default to academic constraint

    # Step 1: Prepare graph + embeddings
    db = get_db()
    graph = construct_graph(db, cohort=cohort)
    pyg_data = preprocessing(graph)
    pyg_data = generate_embeddings(pyg_data)
    academic_map = get_academic_constraint(db)
    effort_map = get_effort_constraint(db)
    attendance_map = get_attendance_constraint(db)

    # Choose main constraint for optimization
    if option == "perc_academic":
        main_constraint = academic_map
    elif option == "perc_effort":
        main_constraint = effort_map
    elif option == "perc_attendance":
        main_constraint = attendance_map
    else:
        return jsonify({"error": f"Unknown option '{option}'"}), 400

    allocation_result = allocate_students(
        data=pyg_data,
        num_allocations=num_allocations,
        db=db,
        constraint_map=main_constraint,
        all_constraints={
            "perc_academic": academic_map,
            "perc_effort": effort_map,
            "perc_attendance": attendance_map,
        }
    )


    # Step 4: Post-process
    full_json_dict = fetch_student_dict_from_id(db, allocation_result)
    convert_data_in_graph_cluster(allocation_result, pyg_data, graph, db, full_json_dict["Run_Number"])

    # Merge the average scores into the final result
    full_json_dict["AveragePerformance"] = allocation_result.get("AveragePerformance", {})
    return jsonify(full_json_dict)

@pipeline_bp.route("/random_allocation", methods=['GET'])
def run_random_allocation():
    db = get_db()
    num_allocations = int(request.args.get('classroomCount', 4))
    cohort = request.args.get('cohort', None)
    if cohort is not None:
        try:
            cohort = int(cohort)
        except ValueError:
            pass

    allocation_data = random_classroom_allocator(num_allocations, db, cohort=cohort)
    full_json_dict = fetch_student_dict_from_id(db, allocation_data)
    return jsonify(full_json_dict)

@main_bp.route("/allocation-runs", methods=["GET"])
def get_allocation_runs():
    runs_path = os.path.join("SchoolData")
    try:
        files = os.listdir(runs_path)
        run_files = [f for f in files if f.endswith(".xlsx") or f.endswith(".csv")]
        run_names = [os.path.splitext(f)[0] for f in run_files]
        return jsonify({"runs": run_names})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from flask import Blueprint, jsonify
import os

# main_bp = Blueprint("main_bp", __name__)

# @main_bp.route("/allocation-runs", methods=["GET"])
# def get_allocation_runs():
#     runs_path = os.path.join("SchoolData")
#     try:
#         files = os.listdir(runs_path)
#         run_files = [f for f in files if f.endswith(".xlsx") or f.endswith(".csv")]
#         run_names = [os.path.splitext(f)[0] for f in run_files]
#         return jsonify({"runs": run_names})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@main_bp.route("/group-relationship-summary", methods=["GET"])
def group_relationship_summary():
    # Example mock data - replace with actual database logic
    summary = {
        "avg_friendship_retained": "72%",
        "avg_engagement_score": 3.8,
        "avg_stability": "65%",
        "avg_behavior_rating": 4.1
    }
    return jsonify(summary)
