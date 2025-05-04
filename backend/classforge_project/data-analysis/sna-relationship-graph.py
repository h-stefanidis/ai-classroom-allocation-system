from flask import Flask, jsonify
import pandas as pd
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

app = Flask(__name__)

# Load Excel and networks
excel_path = "../backend/classforge_project/SchoolData/Student_Survey_AllSheets_Updated.xlsx"
network_sheets = {
    "friend": "net_0_Friends",
    "influence": "net_1_Influential",
    "feedback": "net_2_Feedback",
    "more_time": "net_3_MoreTime",
    "advice": "net_4_Advice",
    "disrespect": "net_5_Disrespect"
}

network_analysis = {}

def load_networks():
    xls = pd.ExcelFile(excel_path)
    for key, sheet in network_sheets.items():
        df = xls.parse(sheet)
        df.columns = df.columns.str.strip()
        df.dropna(subset=[df.columns[0], df.columns[1]], inplace=True)

        G = nx.DiGraph()
        G.add_edges_from(df.values)

        network_analysis[key] = {
            "graph": G
        }

# Convert graph to JSON-friendly format
def serialize_graph(G):
    pos = nx.spring_layout(G, seed=42, k=0.15)
    community = nx.get_node_attributes(G, "community")

    nodes = [
        {
            "id": int(n),
            "label": str(n),
            "x": float(pos[n][0]),
            "y": float(pos[n][1]),
            "community": community.get(n, None)
        }
        for n in G.nodes()
    ]

    edges = [
        {
            "source": int(u),
            "target": int(v)
        }
        for u, v in G.edges()
    ]

    return {"nodes": nodes, "edges": edges}

@app.route("/friend-network-graph", methods=["GET"])
def get_friend_network():
    try:
        G = network_analysis["friend"]["graph"]

        # Assign community if not already present
        if not nx.get_node_attributes(G, "community"):
            communities = list(greedy_modularity_communities(G.to_undirected()))
            for i, community in enumerate(communities):
                for node in community:
                    G.nodes[node]["community"] = i

        data = serialize_graph(G)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    load_networks()
    app.run(debug=True)


# React code
"""
import React, { useEffect, useRef } from "react";
import { Network } from "vis-network/standalone";
import axios from "axios";

const FriendNetworkGraph = () => {
  const containerRef = useRef(null);

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        const res = await axios.get("http://localhost:5000/friend-network-graph");
        const { nodes, edges } = res.data;

        const data = {
          nodes: nodes.map(n => ({
            id: n.id,
            label: n.label,
            x: n.x * 500, // scale for better visibility
            y: n.y * 500,
            group: n.community
          })),
          edges: edges
        };

        const options = {
          physics: false,
          layout: { improvedLayout: false },
          interaction: { hover: true, zoomView: true }
        };

        new Network(containerRef.current, data, options);
      } catch (err) {
        console.error("Failed to fetch graph:", err);
      }
    };

    fetchGraph();
  }, []);

  return (
    <div>
      <h2>Friend Network Graph</h2>
      <div ref={containerRef} style={{ height: "600px", border: "1px solid #ccc" }} />
    </div>
  );
};

export default FriendNetworkGraph;


"""