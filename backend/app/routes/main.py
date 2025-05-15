from ml.build_graph_from_db import build_graph_from_db
from ml.cluster_with_gnn_with_constraints import cluster_students_with_gnn
from ml.export_clusters import export_clusters
from ml.fetch_student_name_from_id import fetch_student_name_from_id
from ml.preserved_relationship import compute_preserved_relationships
from flask import Blueprint, request, jsonify
from db.db_manager import get_db
import uuid
#from db import get_session
from db.db_usage import (
    get_latest_allocations_from_db,
    update_classroom_allocations,
    drop_allocations_table,
    create_allocations_table,
    populate_allocations_table,
    save_allocations_to_db,
    generate_run_number,
    fetch_student_dict_from_id
)

from ml.model_2.construct_graph import construct_graph
from ml.model_2.graph_splitting import attach_names_to_graph, get_split_graphs


from flask_cors import cross_origin



pipeline_bp = Blueprint("pipeline", __name__)

@pipeline_bp.route("/get_allocation", methods=['GET'])  
def run_samsun_model_pipeline():    
    db=get_db()
    #if not db.is_active:
    #    db = create_new_session()

    classroom_count = int(request.args.get('classroom_count', 4))
    graph = build_graph_from_db(db, 2025)
    clustered_data, graph = cluster_students_with_gnn(graph, classroom_count)


    print(clustered_data)
    json_data = export_clusters(clustered_data)

    generate_run_number()
    full_json_dict = fetch_student_dict_from_id(db, json_data)
    save_allocations_to_db(db, full_json_dict)
    
    # Save relationship data
    #compute_preserved_relationships(db, clustered_data, json_with_student_name["Run_Number"])

    return jsonify(full_json_dict)
    # Step 3: Update db with classroom info 
    #return jsonify({"output": final_output})

# run_samsun_model_pipeline()


@cross_origin(origin='http://localhost:3000')
@pipeline_bp.route("/cytoscape_subgraphs", methods=['GET'])  
def cytoscape_subgraphs():
    db=get_db()
    graph = construct_graph(db)
    allocations = get_latest_allocations_from_db(db)
    data = get_split_graphs(graph, allocations)
    return jsonify(data)

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, origins="http://localhost:3000")

from db.db_usage import classroom_update  # make sure it's imported

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
                classroom_id = int(classroom_label.split("_")[1])  # e.g., "Classroom_3" -> 3
            except (IndexError, ValueError):
                return jsonify({"error": f"Invalid classroom format: {classroom_label}"}), 400

            for student_id in student_ids:
                update_values.append((student_id, classroom_id))
                #print(classroom_id)
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
