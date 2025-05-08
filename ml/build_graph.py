import pandas as pd
import torch
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from torch_geometric.data import Data
from sklearn.metrics.pairwise import cosine_similarity

EDGE_TYPE = {
    "friend": 0,
    "influence": 1,
    "feedback": 2,
    "more_time": 3,
    "advice": 4,
    "disrespect": 5
}

def build_graph_from_dataframe(
    participants: pd.DataFrame,
    friends_df: pd.DataFrame,
    influential_df: pd.DataFrame,
    feedback_df: pd.DataFrame,
    more_time_df: pd.DataFrame,
    advice_df: pd.DataFrame,
    disrespect_df: pd.DataFrame,
):
    participants = participants.dropna(subset=["participant_id"])

    id_to_index = {pid: idx for idx, pid in enumerate(participants["participant_id"])}
    num_nodes = len(participants)

    feature_cols = ["perc_effort", "attendance", "perc_academic", "complete_years"]
    if "house" in participants.columns:
        participants["house"] = participants["house"].astype("category").cat.codes
        feature_cols.append("house")

    for col in feature_cols:
        participants[col] = pd.to_numeric(participants[col], errors="coerce").fillna(0)

    scaler = StandardScaler()
    features = scaler.fit_transform(participants[feature_cols])
    x = torch.tensor(features, dtype=torch.float)

    edge_index = []
    edge_type = []

 
    # Add edges from each relationship dataframe
    def add_edges(df, relation):
        for _, row in df.iterrows():
            source_id = row.get("source")
            if pd.isna(source_id) or source_id not in id_to_index:
                continue
            source_idx = id_to_index[int(source_id)]

            for col in df.columns:
                if col == "source":
                    continue
                target_id = row.get(col)
                if pd.isna(target_id) or target_id not in id_to_index:
                    continue
                target_idx = id_to_index[int(target_id)]
                edge_index.append([source_idx, target_idx])
                edge_type.append(EDGE_TYPE[relation])


    add_edges(friends_df, "friend")
    add_edges(influential_df, "influence")
    add_edges(feedback_df, "feedback")
    add_edges(more_time_df, "more_time")
    add_edges(advice_df, "advice")
    add_edges(disrespect_df, "disrespect")

    if edge_index:
        edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
        edge_type = torch.tensor(edge_type, dtype=torch.long)
    else:
        edge_index = torch.empty((2, 0), dtype=torch.long)
        edge_type = torch.empty((0,), dtype=torch.long)

    y = torch.randint(0, 3, (num_nodes,), dtype=torch.long)
    data = Data(x=x, edge_index=edge_index, edge_type=edge_type, y=y)

    save_path = Path(__file__).resolve().parent.parent / "data" / "student_graph.pt"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(data, save_path)

    print("Graph saved to data/student_graph.pt")
    print(f"- Nodes: {x.shape[0]}, Features: {x.shape[1]}")
    print(f"- Edges: {edge_index.shape[1]}, Edge types: {len(set(edge_type.tolist())) if len(edge_type) > 0 else 0}")
