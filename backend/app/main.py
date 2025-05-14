from ml.model_2.graph_conversion import preprocessing
from ml.model_2.construct_graph import construct_graph
from ml.model_2.model2 import generate_embeddings
from ml.model_2.allocation import allocate_students
from db.db_manager import get_db

if __name__ == "__main__":
    with get_db() as db:
        # Step 1: Construct and preprocess graph
        social_network_graph = construct_graph(db, cohort='2025')
        pyg_data = preprocessing(social_network_graph)

        # Step 2: Generate and attach embeddings
        pyg_data = generate_embeddings(pyg_data)

        # Step 3: Allocate students
        allocations = allocate_students(pyg_data, num_allocations=3, db=db)

        # Step 4: Print allocations
        print(allocations)