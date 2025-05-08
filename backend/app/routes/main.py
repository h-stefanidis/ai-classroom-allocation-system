from ml.pipeline.data_prep import preprocess_data
from ml.pipeline.graph_builder import build_graph
from ml.pipeline.model_runner import run_model
from ml.pipeline.postprocessing import postprocess_results
from flask import Blueprint, request, jsonify

pipeline_bp = Blueprint("pipeline", __name__)

@pipeline_bp.route("/run_pipeline", methods=['POST'])
def run_pipeline():
    data = request.get_json()
    num_classrooms = data.get("num_classrooms")

    if num_classrooms is None:
        return jsonify({"error": "num_classrooms not provided"}), 400

    # Step 1: Preprocess
    #df = preprocess_data()

    # Step 2: Build graph
    graph = build_graph(df)

    # Step 3: Run model
    results = run_model(graph, num_classrooms)

    # Step 4: Post-process
    final_output = postprocess_results(results, df)

    return jsonify({"output": final_output})
