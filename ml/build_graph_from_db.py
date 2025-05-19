import pandas as pd
import torch
import json
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from torch_geometric.data import Data
from sqlalchemy import create_engine
# from db_config import load_db_url
from pathlib import Path
import uuid
# from db.db_manager import get_db



#def load_db_url(config_path="database/config.json"):
#    with open(config_path, "r") as f:
#        config = json.load(f)["database"]
#    user = config["user"]
#    password = config["password"]
#    host = config["host"]
#    port = config["port"]
#    dbname = config["dbname"]
#    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

def build_graph_from_db(db,cohort=None):
    #engine = create_engine(db_url)

    ## === Load participants ===
    ## include cohort filtering later
    #query = """
    #    SELECT 
    #        participant_id,
    #        perc_effort,
    #        attendance,
    #        perc_academic,
    #        complete_years,
    #        house
    #    FROM raw.participants
    #    WHERE participant_id IS NOT NULL
    #"""
    #participants = pd.read_sql(query, engine)
    #participants["participant_id"] = participants["participant_id"].astype(int)

     #Fetch participant data of respective cohort if any for node features

    EDGE_TYPE = {
        "friend": 0,
        "influence": 1,
        "feedback": 2,
        "more_time": 3,
        "advice": 4,
        "disrespect": 5
    }

    network_tables = {
        "friend": "raw.friends",
        "influence": "raw.influential",
        "feedback": "raw.feedback",
        "more_time": "raw.more_time",
        "advice": "raw.advice",
        "disrespect": "raw.disrespect"
    }

    participants_query = """
        SELECT participant_id, perc_academic, perc_effort, attendance, complete_years, cohort 
        FROM raw.participants
        """ + (f" WHERE cohort = '{cohort}'" if cohort else "")
    participants = db.query_df(participants_query)
    print(participants,"-------------")

    participants["participant_id"] = participants["participant_id"].astype(int)

    id_to_index = {pid: idx for idx, pid in enumerate(participants["participant_id"])}
    num_nodes = len(participants)
    # === Feature processing ===
    feature_cols = ["perc_effort", "attendance", "perc_academic", "complete_years"]
    if "house" in participants.columns:
        participants["house"] = participants["house"].astype("category").cat.codes
        feature_cols.append("house")

    for col in feature_cols:
        participants[col] = pd.to_numeric(participants[col], errors="coerce").fillna(0)

    scaler = StandardScaler()
    x = torch.tensor(scaler.fit_transform(participants[feature_cols]), dtype=torch.float)

    # === Build edges ===
    edge_index = []
    edge_type = []

    def add_edges(df, relation):
        for _, row in df.iterrows():
            src = row["source"]
            tgt = row["target"]
            if pd.isna(src) or pd.isna(tgt):
                continue
            if src not in id_to_index or tgt not in id_to_index:
                continue
            edge_index.append([id_to_index[int(src)], id_to_index[int(tgt)]])
            edge_type.append(EDGE_TYPE[relation])

    for relation, table in network_tables.items():
        #df = pd.read_sql(f"SELECT source, target FROM {table}", engine)
        relation_query = f"SELECT source, target FROM {table}"
        df = db.query_df(relation_query)
        add_edges(df, relation)

    if edge_index:
        edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
        edge_type = torch.tensor(edge_type, dtype=torch.long)
    else:
        edge_index = torch.empty((2, 0), dtype=torch.long)
        edge_type = torch.empty((0,), dtype=torch.long)

    y = torch.randint(0, 3, (num_nodes,), dtype=torch.long)
    graph = Data(x=x, edge_index=edge_index, edge_type=edge_type, y=y)
    graph.participant_ids = torch.tensor(participants["participant_id"].values, dtype=torch.long)

    #torch.save(data, "data/student_graph.pt")
    #print("Graph saved to data/student_graph.pt")
    print(f"- Nodes: {x.shape[0]}, Features: {x.shape[1]}")
    print(f"- Edges: {edge_index.shape[1]}, Edge types: {len(set(edge_type.tolist())) if len(edge_type) > 0 else 0}")

    return graph

#if __name__ == "__main__":
#    # with get_db() as db:
#    #     initial_graph = build_graph_from_db(db, '2025')

#    db_url = load_db_url()
#    initial_graph = build_graph_from_db(db_url)

