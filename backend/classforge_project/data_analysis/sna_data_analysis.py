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

def analyze_networks_from_db(cohort="2025"):
    """
    Performs SNA metrics (degree, betweenness) for each relationship type,
    filtered by the given student cohort, and includes student names.
    """
    network_analysis = {}

    # Load participants and build a name map
    participants_df = db.query_df("SELECT participant_id, first_name, last_name FROM raw.participants WHERE cohort = %s", (cohort,))
    name_map = {
        row["participant_id"]: f"{row['first_name']} {row['last_name']}"
        for _, row in participants_df.iterrows()
    }

    for name, fetch_func in network_db_fetchers.items():
        df = fetch_func(cohort)
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
            "top_in_degree": [
                {
                    "node": int(n),
                    "name": name_map.get(int(n), "Unknown"),
                    "value": int(v)
                } for n, v in sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:5]
            ],
            "top_out_degree": [
                {
                    "node": int(n),
                    "name": name_map.get(int(n), "Unknown"),
                    "value": int(v)
                } for n, v in sorted(out_degree.items(), key=lambda x: x[1], reverse=True)[:5]
            ],
            "top_betweenness": [
                {
                    "node": int(n),
                    "name": name_map.get(int(n), "Unknown"),
                    "value": float(v)
                } for n, v in sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
            ],
        }

    return network_analysis

def generate_sna_summary_per_classroom(run_number, db):
    if not run_number:
        latest_run = db.query_df("""
            SELECT run_number 
            FROM public.classroom_allocation 
            ORDER BY id DESC 
            LIMIT 1
        """)
        if latest_run.empty:
            return {"error": "No run_number found in classroom_allocation table."}, 404
        run_number = latest_run.iloc[0]["run_number"]

    edge_df = db.query_df("SELECT * FROM public.edge_relationship WHERE run_number = %s", (run_number,))
    alloc_df = db.query_df("SELECT * FROM public.classroom_allocation WHERE run_number = %s", (run_number,))
    if edge_df.empty or alloc_df.empty:
        return {"error": f"No data found for run_number {run_number}"}, 404

    participants_df = db.query_df("SELECT participant_id, first_name, last_name FROM raw.participants")
    name_map = {
        row["participant_id"]: f"{row['first_name']} {row['last_name']}"
        for _, row in participants_df.iterrows()
    }

    import networkx as nx
    classroom_sna_summary = []

    for classroom_id in alloc_df['classroom_id'].unique():
        students = alloc_df[alloc_df['classroom_id'] == classroom_id]['participant_id'].tolist()
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
            "run_number": str(run_number),
            "classroom_id": int(classroom_id),
            "num_nodes": int(G.number_of_nodes()),
            "num_edges": int(G.number_of_edges()),
            "top_in_degree": [{"node": int(k), "name": name_map.get(int(k), "Unknown"), "value": int(v)} for k, v in sorted(in_deg.items(), key=lambda x: x[1], reverse=True)[:5]],
            "top_out_degree": [{"node": int(k), "name": name_map.get(int(k), "Unknown"), "value": int(v)} for k, v in sorted(out_deg.items(), key=lambda x: x[1], reverse=True)[:5]],
            "top_betweenness": [{"node": int(k), "name": name_map.get(int(k), "Unknown"), "value": float(v)} for k, v in sorted(btw.items(), key=lambda x: x[1], reverse=True)[:5]],
        }

        classroom_sna_summary.append(summary)

    return classroom_sna_summary

def generate_sna_summary_per_classroom_by_relationship(run_number, db):
    if not run_number:
        latest_run = db.query_df("""
            SELECT run_number 
            FROM public.classroom_allocation 
            ORDER BY id DESC 
            LIMIT 1
        """)
        if latest_run.empty:
            return {"error": "No run_number found in classroom_allocation table."}, 404
        run_number = latest_run.iloc[0]["run_number"]

    alloc_df = db.query_df("SELECT * FROM public.classroom_allocation WHERE run_number = %s", (run_number,))
    if alloc_df.empty:
        return {"error": f"No classroom data found for run_number {run_number}"}, 404

    participants_df = db.query_df("SELECT participant_id, first_name, last_name FROM raw.participants")
    name_map = {
        row["participant_id"]: f"{row['first_name']} {row['last_name']}"
        for _, row in participants_df.iterrows()
    }

    relationship_types = ["friend", "influence", "feedback", "more_time", "advice", "disrespect"]
    all_relationship_summaries = {}

    for rel_type in relationship_types:
        edge_df = db.query_df(f"""
            SELECT source_id, target_id
            FROM public.edge_relationship
            WHERE run_number = %s AND relationship_type = %s
        """, (run_number, rel_type))

        if edge_df.empty:
            all_relationship_summaries[rel_type] = []
            continue

        classroom_sna_summary = []
        for classroom_id in alloc_df['classroom_id'].unique():
            students = alloc_df[alloc_df['classroom_id'] == classroom_id]['participant_id'].tolist()
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
                "run_number": str(run_number),
                "relationship_type": rel_type,
                "classroom_id": int(classroom_id),
                "num_nodes": int(G.number_of_nodes()),
                "num_edges": int(G.number_of_edges()),
                "top_in_degree": [{"node": int(k), "name": name_map.get(int(k), "Unknown"), "value": int(v)} for k, v in sorted(in_deg.items(), key=lambda x: x[1], reverse=True)[:5]],
                "top_out_degree": [{"node": int(k), "name": name_map.get(int(k), "Unknown"), "value": int(v)} for k, v in sorted(out_deg.items(), key=lambda x: x[1], reverse=True)[:5]],
                "top_betweenness": [{"node": int(k), "name": name_map.get(int(k), "Unknown"), "value": float(v)} for k, v in sorted(btw.items(), key=lambda x: x[1], reverse=True)[:5]],
            }

            classroom_sna_summary.append(summary)

        all_relationship_summaries[rel_type] = classroom_sna_summary

    return all_relationship_summaries


# print(str(analyze_networks_from_db()))

