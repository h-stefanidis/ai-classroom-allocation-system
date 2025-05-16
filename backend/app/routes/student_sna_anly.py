
from flask import Blueprint, request, jsonify, session
from functools import wraps
from backend.classforge_project.data_analysis.sna_data_analysis import *
from backend.classforge_project.data_analysis.sna_relationship_graph import *
from backend.classforge_project.data_analysis.sna_relationship_graph import network_analysis
from db.db_manager import get_db


# Create a Blueprint for authentication routess
sna_bp = Blueprint('sna', __name__)



"""
Example response:
Nodes: Number of unique students involved in each network.

Edges: Number of directed connections (e.g., "Student A selected B as a friend").

Top In-Degree: Students most frequently nominated by others (popularity/influence).

Top Out-Degree: Students who nominated many others (active or seeking).

Top Betweenness: Students acting as bridges between groups (social connectors).
{
  "friend": {
    "num_nodes": 675,
    "num_edges": 4739,
    "top_in_degree": [
      { "node": 32407, "value": 26 },
      { "node": 32405, "value": 23 }
    ],
    "top_out_degree": [
      { "node": 32409, "value": 35 },
      { "node": 32534, "value": 23 }
    ],
    "top_betweenness": [
      { "node": 1182, "value": 0.01478 },
      { "node": 32409, "value": 0.01418 }
    ]
  },
  "influence": {
    "num_nodes": 673,
    "num_edges": 1722,
    ...
  }
}

"""
@sna_bp.route("/sna_summary_acc_to_cohort", methods=["GET"])
def sna_summary():
    try:
        # Get cohort from query params, default to 2025
        cohort = request.args.get("cohort", "2025")

        result = analyze_networks_from_db(cohort)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sna_bp.route("/sna_by_run_number", methods=["GET"])
def sna_summary_by_run():
    """
    Analyze SNA metrics per classroom for a given run_number.
    If no run_number is provided, uses the most recent run based on classroom_allocation.created_at.
    Returns: JSON object with top centrality metrics by classroom.
    """
    db = get_db()

    # Try to get run_number from request, else find the latest one
    run_number = request.args.get("run_number")

    try:

        sna_per_class = generate_sna_summary_per_classroom(run_number, db)
        return jsonify(sna_per_class)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sna_bp.route("/sna_by_run_number_in_types_of_relationship", methods=["GET"])
def sna_summary_per_classroom_by_relationship():
    """
    Analyze SNA metrics per classroom for a given run_number.
    If no run_number is provided, uses the most recent run based on classroom_allocation.created_at.
    Returns: JSON object with top centrality metrics by classroom with different types of relationship.
    """
    db = get_db()

    # Try to get run_number from request, else find the latest one
    run_number = request.args.get("run_number")

    try:

        sna_per_class = generate_sna_summary_per_classroom_by_relationship(run_number, db)
        return jsonify(sna_per_class)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sna_bp.route("/friend-network-graph", methods=["GET"])
def get_dynamic_network_graph():
    """
    Returns network graph data for a specific relationship type and run number.
    """
    relationship_type = request.args.get("type", "friend")
    run_number = request.args.get("run_number")

    if not run_number:
        return jsonify({"error": "run_number is required"}), 400

    fetch_func = network_fetchers.get(relationship_type)
    if not fetch_func:
        return jsonify({"error": f"Unknown relationship type: {relationship_type}"}), 400

    df = fetch_func()
    if df is None or df.empty:
        return jsonify({"error": f"No data found for {relationship_type}"}), 404

    df.columns = df.columns.str.strip()
    df.dropna(subset=[df.columns[0], df.columns[1]], inplace=True)

    # Filter by run_number if available in your data
    if "run_number" in df.columns:
        df = df[df["run_number"] == run_number]

    G = nx.DiGraph()
    G.add_edges_from(df.iloc[:, :2].values.tolist())

    # Compute communities
    if not nx.get_node_attributes(G, "community"):
        communities = list(greedy_modularity_communities(G.to_undirected()))
        for i, community in enumerate(communities):
            for node in community:
                G.nodes[node]["community"] = i

    return jsonify(serialize_graph(G))
