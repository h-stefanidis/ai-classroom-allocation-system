#!/bin/bash

touch ml/__init__.py
touch db/__init__.py

set -e  # Exit immediately if a command exits with a non-zero status
trap 'echo "❌ Script failed at step $STEP."' ERR

STEP="1: Building graph"
echo "📦 Step $STEP..."
python db/db_usage.py
echo "✅ Step $STEP complete."
echo "------------------------------"
sleep 1

STEP="2: Clustering with GNN + constraints"
echo "🧠 Step $STEP..."
python ml/cluster_with_gnn_with_constraints.py
echo "✅ Step $STEP complete."
echo "------------------------------"
sleep 1

STEP="3: Exporting clustered data (CSV + JSON)"
echo "📤 Step $STEP..."
python ml/export_clusters.py
echo "✅ Step $STEP complete."
echo "------------------------------"
sleep 1

STEP="4: Inspecting the clustered graph"
echo "🔍 Step $STEP..."
python ml/inspect_clustered_graph.py
echo "✅ Step $STEP complete."
echo "------------------------------"
sleep 1

STEP="5: Evaluating model performance"
echo "📊 Step $STEP..."
python ml/evaluate_model.py
echo "✅ Step $STEP complete."
echo "------------------------------"
sleep 1

echo "🎉 ✅ All steps completed successfully!"
