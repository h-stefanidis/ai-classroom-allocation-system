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


# print(str(analyze_networks_from_db()))

