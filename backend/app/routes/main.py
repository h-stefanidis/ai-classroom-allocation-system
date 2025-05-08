from ml.build_graph_from_db import build_graph_from_db
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


    ## Step 3: Run model
    results = run_model(graph, num_classrooms)

    ## Step 4: Post-process
    #final_output = postprocess_results(results, df)

    #return jsonify({"output": final_output})

run_pipeline()