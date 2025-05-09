import networkx as nx
from db.db_manager import get_db
import matplotlib.pyplot as plt

def construct_graph(db,cohort=None):
    """
    Constructs a unified directed graph from multiple relationship tables for social network analysis.

    Args:
        db (Database): An instance of the Database class for querying data.

    Returns:
        nx.DiGraph: A directed graph with nodes and edges representing students and their relationships.
    """
    # Define the mapping of edge types
    edge_type_map = {'friends': 0, 'advice': 1, 'disrespect': 2, 'feedback': 3, 'influential': 4}

    # Initialize a directed graph
    graph = nx.DiGraph()

    # Fetch participant data of respective cohort if any for node features 
    participants_query = """
    SELECT participant_id, perc_academic, perc_effort, attendance, cohort
    FROM raw.participants
    """ + (f" WHERE cohort = '{cohort}'" if cohort else "")
    df_participants = db.query_df(participants_query)

    # Add nodes with features
    for _, row in df_participants.iterrows():
        graph.add_node(
            row['participant_id'],
            perc_academic=row['perc_academic'],
            perc_effort=row['perc_effort'],
            attendance=row['attendance']
        )

    # Iterate over each relationship table to add edges
    for table_name, edge_type in edge_type_map.items():
        relationship_query = f"SELECT source, target FROM raw.{table_name}"
        df_relationships = db.query_df(relationship_query)

        for _, row in df_relationships.iterrows():
            graph.add_edge(
                row['source'],
                row['target'],
                edge_type=edge_type
            )

    return graph

def visualize_graph(graph):
    """
    Visualizes the directed graph using matplotlib.

    Args:
        graph (nx.DiGraph): The directed graph to visualize.
    """
    plt.figure(figsize=(12, 8))

    # Draw the graph
    pos = nx.spring_layout(graph)  # Position nodes using the spring layout
    nx.draw(
        graph,
        pos,
        with_labels=True,
        node_size=700,
        node_color="lightblue",
        font_size=10,
        font_color="black",
        edge_color="gray",
        arrowsize=20,
    )

    # Add edge labels for edge_type
    edge_labels = nx.get_edge_attributes(graph, "edge_type")
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    # Show the graph
    plt.title("Social Network Graph")
    plt.show()

if __name__ == "__main__":
    with get_db() as db:
        social_network_graph = construct_graph(db,'2025')
        # visualize_graph(social_network_graph)
        print(f"Graph constructed with {social_network_graph.number_of_nodes()} nodes and {social_network_graph.number_of_edges()} edges.")
        visualize_graph(social_network_graph.subgraph(['student_id_1', 'student_id_2', 'student_id_3']))
        