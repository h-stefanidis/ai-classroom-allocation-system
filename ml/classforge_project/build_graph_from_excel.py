import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler
from torch_geometric.data import Data

EDGE_TYPE = {
    "friend": 0,
    "influence": 1,
    "feedback": 2,
    "more_time": 3,
    "advice": 4,
    "disrespect": 5
}

network_sheets = {
    "friend": "net_0_Friends",
    "influence": "net_1_Influential",
    "feedback": "net_2_Feedback",
    "more_time": "net_3_MoreTime",
    "advice": "net_4_Advice",
    "disrespect": "net_5_Disrespect"
}

def build_graph_from_excel(file_path):
    xl = pd.ExcelFile(file_path)
    participants = xl.parse("participants")
    participants = participants.dropna(subset=["Participant-ID"])
    participants["Participant-ID"] = participants["Participant-ID"].astype(int)

    id_to_index = {pid: idx for idx, pid in enumerate(participants["Participant-ID"])}
    num_nodes = len(participants)

    # Feature columns based on your input
    feature_cols = ["Perc_Effort", "Attendance", "Perc_Academic", "CompleteYears"]

    # Encode 'House' as categorical if present
    if "House" in participants.columns:
        participants["House"] = participants["House"].astype("category").cat.codes
        feature_cols.append("House")

    # Fill missing values
    participants[feature_cols] = participants[feature_cols].fillna(0)

    # Normalize features
    scaler = StandardScaler()
    features = participants[feature_cols]
    x = torch.tensor(scaler.fit_transform(features), dtype=torch.float)

    edge_index = []
    edge_type = []

    for relation, sheet in network_sheets.items():
        df = xl.parse(sheet)

        for _, row in df.iterrows():
            source_id = row.get("Source")
            if pd.isna(source_id) or source_id not in id_to_index:
                continue
            source_idx = id_to_index[int(source_id)]

            for target_col in df.columns[1:]:
                target_id = row.get(target_col)
                if pd.isna(target_id) or target_id not in id_to_index:
                    continue
                target_idx = id_to_index[int(target_id)]
                edge_index.append([source_idx, target_idx])
                edge_type.append(EDGE_TYPE[relation])

    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
    edge_type = torch.tensor(edge_type, dtype=torch.long)

    y = torch.randint(0, 3, (num_nodes,))  # Replace with real classroom labels if available

    data = Data(x=x, edge_index=edge_index, edge_type=edge_type, y=y)
    # participant_ids = torch.tensor(participants["Participant-ID"].values, dtype=torch.long)
    # data = Data(x=x, edge_index=edge_index, edge_type=edge_type, y=y)
    # data.participant_ids = participant_ids

    torch.save(data, "data/student_graph.pt")
    print("✅ Graph saved to data/student_graph.pt with shape:")
    print(f"- Nodes: {x.shape[0]}, Features: {x.shape[1]}")
    print(f"- Edges: {edge_index.shape[1]}, Edge types: {len(set(edge_type.tolist()))}")

if __name__ == "__main__":
    build_graph_from_excel("SchoolData/Student Survey - Jan.xlsx")
