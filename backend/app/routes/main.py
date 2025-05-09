from ml.build_graph_from_db import build_graph_from_db
from ml.cluster_with_gnn_with_constraints import cluster_students_with_gnn
from ml.export_clusters import export_clusters
from flask import Blueprint, request, jsonify
from db.db_manager import get_db
from db.db_usage import (
    update_classroom_allocations,
    drop_allocations_table,
    create_allocations_table,
    populate_allocations_table,
)

pipeline_bp = Blueprint("pipeline", __name__)

@pipeline_bp.route("/run_samsun_model_pipeline", methods=['POST'])
def run_samsun_model_pipeline():
    #data = request.get_json()
    #num_classrooms = data.get("num_classrooms")

    #if num_classrooms is None:
    #    return jsonify({"error": "num_classrooms not provided"}), 400

    # Step 1: Preprocess
    #df = preprocess_data()

    # Just incase, to redo the allocations table as 0 classroom alloc

    #drop_allocations_table()
    #create_allocations_table()
    #populate_allocations_table()


    # Step 2: Build graph and export clusters
    db=get_db()
    graph = build_graph_from_db(db, 2025)
    clustered_data, graph = cluster_students_with_gnn(graph, 4)
    json_data = export_clusters(clustered_data)

    update_classroom_allocations(json_data) # Update allocations table

    # Step 3: Update db with classroom info 

    #print(json_data)

    ## Step 4: Post-process
    #final_output = postprocess_results(results, df)

    #return jsonify({"output": final_output})

run_samsun_model_pipeline()
