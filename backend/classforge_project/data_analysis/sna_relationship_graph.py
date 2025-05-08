import pandas as pd
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
from flask import jsonify

from db.db_usage import (
    get_all_friends, get_all_influential, get_all_feedback,
    get_all_more_time, get_all_advice, get_all_disrespect
)

network_analysis = {}

network_fetchers = {
    "friend": get_all_friends,
    "influence": get_all_influential,
    "feedback": get_all_feedback,
    "more_time": get_all_more_time,
    "advice": get_all_advice,
    "disrespect": get_all_disrespect
}

def load_networks_from_db():
    for key, fetch_func in network_fetchers.items():
        df = fetch_func()
        if df is None or df.empty:
            continue

        df.columns = df.columns.str.strip()
        df.dropna(subset=[df.columns[0], df.columns[1]], inplace=True)
        edges = df.iloc[:, :2].values.tolist()

        G = nx.DiGraph()
        G.add_edges_from(edges)
        network_analysis[key] = {"graph": G}

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

def get_friend_network_graph():
    if "friend" not in network_analysis:
        load_networks_from_db()

    G = network_analysis["friend"]["graph"]

    if not nx.get_node_attributes(G, "community"):
        communities = list(greedy_modularity_communities(G.to_undirected()))
        for i, community in enumerate(communities):
            for node in community:
                G.nodes[node]["community"] = i

    return jsonify(serialize_graph(G))


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