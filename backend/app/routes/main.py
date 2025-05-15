from ml.build_graph_from_db import build_graph_from_db
from ml.cluster_with_gnn_with_constraints import cluster_students_with_gnn
from ml.export_clusters import export_clusters
from ml.fetch_student_name_from_id import fetch_student_name_from_id
from ml.preserved_relationship import compute_preserved_relationships, save_edge_relationships_db
from flask import Blueprint, request, jsonify
from db.db_manager import get_db
from db.db_usage import (
    update_classroom_allocations,
    drop_allocations_table,
    create_allocations_table,
    populate_allocations_table,
)
import torch

pipeline_bp = Blueprint("pipeline", __name__)

@pipeline_bp.route("/get_allocation", methods=['GET'])
def run_samsun_model_pipeline():


    # Step 2: Build graph and export clusters
    db=get_db()
    graph = build_graph_from_db(db, 2025)
    participant_ids = graph.participant_ids

    # Convert Tensors to plain ints if needed
    participant_ids = [
        pid.item() if isinstance(pid, torch.Tensor) else pid
        for pid in participant_ids
    ]
    clustered_data, graph = cluster_students_with_gnn(graph, 4)

    print(clustered_data)
    json_data = export_clusters(clustered_data)

    update_classroom_allocations(json_data) # Update allocations table

    # Save allocation and fetch student first and last names
    json_with_student_name = fetch_student_name_from_id(db, json_data)


    # Save relationship data
    compute_preserved_relationships(db, clustered_data, json_with_student_name["Run_Number"])
    
    # Save intra-classroom edge-level data
    save_edge_relationships_db(db, clustered_data, json_with_student_name["Run_Number"], participant_ids)

   
    print(json_with_student_name["Run_Number"])
    return jsonify(json_with_student_name)
    # Step 3: Update db with classroom info 

    #print(json_data)

    ## Step 4: Post-process
    #final_output = postprocess_results(results, df)

    #return jsonify({"output": final_output})

run_samsun_model_pipeline()