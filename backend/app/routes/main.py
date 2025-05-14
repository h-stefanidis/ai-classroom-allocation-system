from ml.build_graph_from_db import build_graph_from_db
from ml.cluster_with_gnn_with_constraints import cluster_students_with_gnn
from ml.export_clusters import export_clusters
from ml.fetch_student_name_from_id import fetch_student_name_from_id
from ml.preserved_relationship import compute_preserved_relationships
from flask import Blueprint, request, jsonify
from db.db_manager import get_db

# imports for model2:
from ml.model_2.construct_graph import construct_graph
from ml.model_2.graph_conversion import preprocessing
from ml.model_2.model2 import generate_embeddings
from ml.model_2.allocation import allocate_students


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
@pipeline_bp.route("/run_model2", methods=['GET'])
def run_model2_route():
    """
    Run the Model 2 pipeline: construct graph, convert to PyG, run GNN, allocate students.
    Expects query parameters: 'num_allocations' (int), 'cohort' (int or str)
    """
    # Get query parameters
    num_allocations = int(request.args.get('num_allocations', 3))  # default to 3 if not provided
    cohort = request.args.get('cohort', 2025)  # default to 2025
    db = get_db()
    graph=construct_graph(db,cohort=cohort)
    pyg_data=preprocessing(graph)
    pyg_data=generate_embeddings(pyg_data)
    data= allocate_students(pyg_data, num_allocations=num_allocations, db=db)
    return data

