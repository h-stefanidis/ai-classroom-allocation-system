# Step 1: Load Libraries
import pandas as pd
import networkx as nx
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from collections import defaultdict
from itertools import chain
import matplotlib.pyplot as plt

# Step 2: Load Excel and Parse Sheets
excel_path = "./backend/SchoolData/Student_Survey_AllSheets_Updated.xlsx"
xls = pd.ExcelFile(excel_path)

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

# Step 3: Load and Build Networks
networks = {}
for key, sheet in network_sheets.items():
    df = xls.parse(sheet)
    df.columns = df.columns.str.strip()
    df.dropna(subset=[df.columns[0], df.columns[1]], inplace=True)
    networks[key] = df

# Step 4: Create Composite Graph
G_composite = nx.DiGraph()

positive_networks = ['friend', 'advice']
negative_networks = ['disrespect']

all_nodes = set(chain.from_iterable(G.nodes() for G in [
    nx.from_pandas_edgelist(networks[n], source=networks[n].columns[0], target=networks[n].columns[1], create_using=nx.DiGraph())
    for n in (positive_networks + negative_networks)
]))
G_composite.add_nodes_from(all_nodes)

for net in positive_networks:
    for src, dst in networks[net].values:
        G_composite.add_edge(src, dst, weight=G_composite.get_edge_data(src, dst, {}).get("weight", 0) + 1)

for src, dst in networks['disrespect'].values:
    G_composite.add_edge(src, dst, weight=G_composite.get_edge_data(src, dst, {}).get("weight", 0) - 2)

# Step 5: Load Academic and Wellbeing Data
participants_df = xls.parse("participants")
responses_df = xls.parse("responses")
participants_df.columns = participants_df.columns.str.strip().str.lower()
responses_df.columns = responses_df.columns.str.strip().str.lower()

merged_df = pd.merge(participants_df, responses_df, on="participant-id", how="inner")
selected_features = [
    "participant-id",
    "perc_academic", "perc_effort", "attendance",
    "isolated", "school_support_engage", "comfortable", "bullying"
]
feature_df = merged_df[selected_features].dropna()

scaler = MinMaxScaler()
normalized_features = scaler.fit_transform(feature_df.drop(columns="participant-id"))
normalized_df = pd.DataFrame(normalized_features, columns=selected_features[1:])
normalized_df["participant-id"] = feature_df["participant-id"].values
feature_dict = normalized_df.set_index("participant-id").to_dict(orient="index")

# Step 6: Add Attributes to Graph
valid_ids = set(feature_dict.keys()).intersection(set(G_composite.nodes))
G_filtered = G_composite.subgraph(valid_ids).copy()

for node in G_filtered.nodes():
    G_filtered.nodes[node]["academic_score"] = (
        feature_dict[node]["perc_academic"]
        + feature_dict[node]["perc_effort"]
        + feature_dict[node]["attendance"]
    ) / 3
    G_filtered.nodes[node]["wellbeing_score"] = (
        feature_dict[node]["school_support_engage"]
        + (1 - feature_dict[node]["isolated"])
        + feature_dict[node]["comfortable"]
        - feature_dict[node]["bullying"]
    ) / 4

# Step 7: Assign Groups
sorted_nodes = sorted(G_filtered.nodes, key=lambda x: (
    -G_filtered.nodes[x]["academic_score"], -G_filtered.nodes[x]["wellbeing_score"]
))

group_size = 20
num_groups = len(G_filtered.nodes) // group_size
balanced_groups = defaultdict(list)

for i, node in enumerate(sorted_nodes):
    balanced_groups[i % num_groups].append(node)

# Step 8: Compute Group Stats
group_summary = []
for gid, members in balanced_groups.items():
    score = 0
    positive = negative = 0
    academic_avg = np.mean([G_filtered.nodes[m]["academic_score"] for m in members])
    wellbeing_avg = np.mean([G_filtered.nodes[m]["wellbeing_score"] for m in members])

    for src in members:
        for dst in members:
            if src != dst and G_filtered.has_edge(src, dst):
                w = G_filtered[src][dst]["weight"]
                score += w
                if w > 0:
                    positive += 1
                elif w < 0:
                    negative += 1

    group_summary.append({
        "Group ID": gid,
        "Num Members": len(members),
        "Net Social Score": score,
        "Positive Ties": positive,
        "Negative Ties": negative,
        "Avg Academic Score": round(academic_avg, 2),
        "Avg Wellbeing Score": round(wellbeing_avg, 2)
    })

# Step 9: Output Group Summary
group_summary_df = pd.DataFrame(group_summary).sort_values("Net Social Score", ascending=False)
print(group_summary_df)

# Step 10: Output Group Rosters
group_rosters = []
for group_id, members in balanced_groups.items():
    for student in members:
        group_rosters.append({
            "Group ID": group_id,
            "Student ID": student,
            "Academic Score": round(G_filtered.nodes[student]["academic_score"], 2),
            "Wellbeing Score": round(G_filtered.nodes[student]["wellbeing_score"], 2)
        })

group_rosters_df = pd.DataFrame(group_rosters).sort_values(["Group ID", "Academic Score"], ascending=[True, False])
print(group_rosters_df)
