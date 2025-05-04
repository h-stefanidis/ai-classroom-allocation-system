# from flask import Flask, jsonify
import pandas as pd
import networkx as nx

# app = Flask(__name__)

# File path and configuration
excel_path = "./backend/SchoolData/Student_Survey_AllSheets_Updated.xlsx"

# EDGE_TYPE = {
#     "friend": 0,
#     "influence": 1,
#     "feedback": 2,
#     "more_time": 3,
#     "advice": 4,
#     "disrespect": 5
# }

network_sheets = {
    "friend": "net_0_Friends",
    "influence": "net_1_Influential",
    "feedback": "net_2_Feedback",
    "more_time": "net_3_MoreTime",
    "advice": "net_4_Advice",
    "disrespect": "net_5_Disrespect"
}



def analyze_networks():
    xls = pd.ExcelFile(excel_path)
    networks = {}

    # Load and clean each network sheet
    for key, sheet in network_sheets.items():
        df = xls.parse(sheet)
        df.columns = df.columns.str.strip()
        df.dropna(subset=[df.columns[0], df.columns[1]], inplace=True)
        networks[key] = df

    network_analysis = {}

    # Analyze each network
    for name, df in networks.items():
        G = nx.DiGraph()
        G.add_edges_from(df.values)

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
# @app.route("/sna-summary", methods=["GET"])
# def sna_summary():
#     try:
#         result = analyze_networks()
#         return jsonify(result)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

print(str(analyze_networks()))