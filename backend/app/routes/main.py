from ml.build_graph_from_db import build_graph_from_db
from ml.cluster_with_gnn_with_constraints import cluster_students_with_gnn
from ml.export_clusters import export_clusters
from flask import Blueprint, request, jsonify
from db.db_manager import get_db

pipeline_bp = Blueprint("pipeline", __name__)

@pipeline_bp.route("/run_pipeline", methods=['POST'])
def run_pipeline():
    #data = request.get_json()
    #num_classrooms = data.get("num_classrooms")

    #if num_classrooms is None:
    #    return jsonify({"error": "num_classrooms not provided"}), 400

    # Step 1: Preprocess
    #df = preprocess_data()

    # Step 2: Build graph
    db=get_db()
    graph = build_graph_from_db(db)
    clustered_data = cluster_students_with_gnn(graph)
    json_data = export_clusters(clustered_data)

    print(json_data)




    ## Step 4: Post-process
    #final_output = postprocess_results(results, df)

    #return jsonify({"output": final_output})

run_pipeline()