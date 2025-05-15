from ml.build_graph_from_db import build_graph_from_db
from ml.cluster_with_gnn_with_constraints import cluster_students_with_gnn
from ml.export_clusters import export_clusters
from ml.fetch_student_name_from_id import fetch_student_name_from_id
from ml.preserved_relationship import compute_preserved_relationships, save_edge_relationships_db
from flask import Blueprint, request, jsonify
from db.db_manager import get_db

# imports for model2:
from ml.model_2.construct_graph import construct_graph
from ml.model_2.graph_conversion import preprocessing
from ml.model_2.model2 import generate_embeddings
from ml.model_2.allocation import allocate_students
from ml.model_2.convert_data_into_graph_cluster import convert_data_in_graph_cluster

# import for random allocation:
from ml.model_2.random_allocator import random_classroom_allocator


import uuid
#from db import get_session
from db.db_usage import (
    update_classroom_allocations,
    drop_allocations_table,
    create_allocations_table,
    populate_allocations_table,
    save_allocations_to_db,
    generate_run_number,
    fetch_student_dict_from_id
)
import torch

pipeline_bp = Blueprint("pipeline", __name__)

@pipeline_bp.route("/get_allocation", methods=['GET'])
def run_samsun_model_pipeline():


    # Step 2: Build graph and export clusters
    db=get_db()

    classroom_count = int(request.args.get('classroom_count', 4))
    graph = build_graph_from_db(db, 2025)
    participant_ids = graph.participant_ids

    # Convert Tensors to plain ints if needed
    participant_ids = [
        pid.item() if isinstance(pid, torch.Tensor) else pid
        for pid in participant_ids
    ]
    clustered_data, graph = cluster_students_with_gnn(graph, classroom_count)


    # Save allocation and fetch student first and last names
    # json_with_student_name = fetch_student_name_from_id(db, json_data)
    json_data = export_clusters(clustered_data)
    full_json_dict = fetch_student_dict_from_id(db, json_data)


    # Save relationship data
    compute_preserved_relationships(db, clustered_data, full_json_dict["Run_Number"])
    
    # Save intra-classroom edge-level data
    save_edge_relationships_db(db, clustered_data, full_json_dict["Run_Number"], participant_ids)

   
    return jsonify(full_json_dict)

# run_samsun_model_pipeline()

@pipeline_bp.route("/run_model2", methods=['GET'])
def run_model2_route():
    """
    Run the Model 2 pipeline: construct graph, convert to PyG, run GNN, allocate students.
    Expects query parameters: 'num_allocations' (int), 'cohort' (int or str)
    """
    # Get query parameters
    num_allocations = int(request.args.get('classroomCount', 4))  # default to 4 if not provided
    # num_allocations= 4
    cohort = request.args.get('cohort', 2025)  # default to 2025
    # cohort= 2025
    db = get_db()
    graph=construct_graph(db,cohort=cohort)
    pyg_data=preprocessing(graph)
    pyg_data=generate_embeddings(pyg_data)
    allocation_result= allocate_students(pyg_data, num_allocations=num_allocations, db=db)
    full_json_dict = fetch_student_dict_from_id(db, allocation_result)
    convert_data_in_graph_cluster(allocation_result,pyg_data,graph, db, full_json_dict["Run_Number"])
    return jsonify(full_json_dict)


@pipeline_bp.route("/random_allocation", methods=['GET'])
def run_random_allocation():
    """
    Randomly assigns students to classrooms.
    Expects query parameters: 'classroomCount' (int), 'cohort' (int or str, optional)
    """
    db = get_db()
    num_allocations = int(request.args.get('classroomCount', 4))
    # num_allocations=4
    cohort = request.args.get('cohort', None)
    # cohort = 2025
    if cohort is not None:
        try:
            cohort = int(cohort)
        except ValueError:
            pass  # keep as string if not int

    allocation_data = random_classroom_allocator(num_allocations, db, cohort=cohort)
    print (allocation_data)
    full_json_dict = fetch_student_dict_from_id(db, allocation_data)
    return jsonify(full_json_dict)



