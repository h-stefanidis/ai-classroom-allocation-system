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
    update_classroom_allocations,
    drop_allocations_table,
    create_allocations_table,
    populate_allocations_table,
    save_allocations_to_db,
    generate_run_number,
    fetch_student_dict_from_id
)

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