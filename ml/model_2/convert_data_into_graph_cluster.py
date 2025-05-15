import torch
from ml.preserved_relationship import compute_preserved_relationships, save_edge_relationships_db
from db.db_usage import generate_run_number


def convert_data_in_graph_cluster(allocation_result,pyg_data, graph, db, run_number):
     # Step 4: Create cluster labels for each student in the same order as pyg_data.student_ids
    student_to_cluster = {}
    for i, (classroom, student_list) in enumerate(allocation_result["Allocations"].items()):
        for student_id in student_list:
            student_to_cluster[int(student_id)] = i  # i is the cluster index

    cluster_labels = [student_to_cluster[int(sid)] for sid in pyg_data.student_ids]
    pyg_data.y = torch.tensor(cluster_labels, dtype=torch.long)  # Required for relationship functions

    # Step 5: Extract edge_type from networkx graph edge attributes
    # edge_attrs = [d['edge_attr'][0] for _, _, d in graph.edges(data=True)]
    edge_attrs = [
    d.get('edge_attr', [d.get('edge_type', 0)])[0]
    for _, _, d in graph.edges(data=True)
    ]
    pyg_data.edge_type = torch.tensor(edge_attrs, dtype=torch.long)  # Required for relationship functions

    # Step 6: Collect participant IDs in same order as nodes
    participant_ids = [int(pid) for pid in pyg_data.student_ids]

    # Step 7: Generate a unique run identifier (you could use a UUID instead if preferred)
    # run_number = generate_run_number()

    # Step 8: Save high-level preserved relationships
    compute_preserved_relationships(db, pyg_data, run_number)

    # Step 9: Save edge-level intra-classroom relationships
    save_edge_relationships_db(db, pyg_data, run_number, participant_ids)