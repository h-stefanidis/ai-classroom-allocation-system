# from flask import Flask, jsonify
import pandas as pd
import networkx as nx
from db.db_usage import *


# Mapping for SNA tables and corresponding DB functions
network_db_fetchers = {
    "friend": get_all_friends,
    "influence": get_all_influential,
    "feedback": get_all_feedback,
    "more_time": get_all_more_time,
    "advice": get_all_advice,
    "disrespect": get_all_disrespect
}

def analyze_networks_from_db():

    network_analysis = {}

    for name, fetch_func in network_db_fetchers.items():
        df = fetch_func()
        if df is None or df.empty:
            print(f"No data for {name}")
            continue

        df.columns = df.columns.str.strip()
        df.dropna(subset=[df.columns[0], df.columns[1]], inplace=True)
        
        G = nx.DiGraph()
        G.add_edges_from(df.iloc[:, :2].values.tolist())

        in_degree = dict(G.in_degree())
        out_degree = dict(G.out_degree())
        betweenness = nx.betweenness_centrality(G)

        network_analysis[name] = {
            "num_nodes": int(G.number_of_nodes()),
            "num_edges": int(G.number_of_edges()),
            "top_in_degree": [{"node": int(n), "value": int(v)} for n, v in sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:5]],
            "top_out_degree": [{"node": int(n), "value": int(v)} for n, v in sorted(out_degree.items(), key=lambda x: x[1], reverse=True)[:5]],
            "top_betweenness": [{"node": int(n), "value": float(v)} for n, v in sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]],
        }

    return network_analysis

# Let's define a new function that analyzes SNA metrics by classroom and run number
def generate_sna_summary_per_classroom(run_number, db):

    if len(run_number)==0:
        latest_run = db.query_df("""
            SELECT run_number 
            FROM public.classroom_allocation 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        if latest_run.empty:
            return jsonify({"error": "No run_number found in classroom_allocation table."}), 404
        run_number = latest_run.iloc[0]["run_number"]


    # Load relevant data for the run
    edge_df = db.query_df("SELECT * FROM public.edge_relationship WHERE run_number = %s", (run_number,))
    alloc_df = db.query_df("SELECT * FROM public.classroom_allocation WHERE run_number = %s", (run_number,))


    if edge_df.empty or alloc_df.empty:

        return jsonify({"error": f"No data found for run_number {run_number}"}), 404

    # Prepare final summary list
    classroom_sna_summary = []
    for classroom_id in alloc_df['classroom_id'].unique():
        students = alloc_df[alloc_df['classroom_id'] == classroom_id]['participant_id'].tolist()

        # Filter edges within that classroom
        sub_edges = edge_df[
            (edge_df['source_id'].isin(students)) &
            (edge_df['target_id'].isin(students))
        ]

        G = nx.DiGraph()
        G.add_edges_from(sub_edges[['source_id', 'target_id']].values)

        in_deg = dict(G.in_degree())
        out_deg = dict(G.out_degree())
        btw = nx.betweenness_centrality(G)

        summary = {
            "run_number": run_number,
            "classroom_id": classroom_id,
            "num_nodes": G.number_of_nodes(),
            "num_edges": G.number_of_edges(),
            "top_in_degree": sorted(in_deg.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_out_degree": sorted(out_deg.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_betweenness": sorted(btw.items(), key=lambda x: x[1], reverse=True)[:5],
        }

        classroom_sna_summary.append(summary)

    return classroom_sna_summary




# print(str(analyze_networks_from_db()))

