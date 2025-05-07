#!/bin/bash

# WIP, run each script separately for now
# as cluster_with_gnn_with_constraints.py needs to be quit manually

echo "📦 Step 1: Building graph..."
python build_graph_from_excel.py 

echo "🧠 Step 2: Clustering with GNN + constraints..."
python cluster_with_gnn_with_constraints.py

echo "📤 Step 3: Exporting clustered data (CSV + JSON)..."
python export_clusters.py

echo "🔍 Step 4: Inspecting the clustered graph..."
python inspect_clustered_graph.py

echo "📊 Step 5: Evaluating model performance..."
python evaluate_model.py

echo "✅ All steps completed!"
