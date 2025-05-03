import pandas as pd
import numpy as np
from faker import Faker

# Load Excel file
xls = pd.ExcelFile("../SchoolData/Student Survey - Jan.xlsx")
original_sheets = xls.sheet_names
original_data = {sheet: xls.parse(sheet) for sheet in original_sheets}

# Clean original responses
responses_df = original_data['responses']
responses_df['Participant-ID'] = responses_df['Participant-ID'].astype(str)
responses_df['Status'] = responses_df['Status'].str.strip().str.lower()
responses_cleaned = responses_df.drop(columns=['question5'], errors='ignore')
likert_cols = responses_cleaned.select_dtypes(include='float64').columns.tolist()
for col in likert_cols:
    responses_cleaned[col].fillna(responses_cleaned[col].median(), inplace=True)

# Simulate 500 new responses
faker = Faker()
np.random.seed(42)
num_new = 500
existing_ids = set(responses_cleaned['Participant-ID'])
new_ids = []
counter = 1000
while len(new_ids) < num_new:
    new_id = str(counter)
    if new_id not in existing_ids:
        new_ids.append(new_id)
    counter += 1

simulated_data = {}
for col in likert_cols:
    simulated_data[col] = np.random.choice(responses_cleaned[col], size=num_new, replace=True)

simulated_data['survey-instance-id'] = list(range(responses_cleaned['survey-instance-id'].max() + 1,
                                                  responses_cleaned['survey-instance-id'].max() + 1 + num_new))
simulated_data['Participant-ID'] = new_ids
simulated_data['Status'] = np.random.choice(responses_cleaned['Status'], size=num_new, replace=True)

simulated_df = pd.DataFrame(simulated_data)
combined_responses = pd.concat([responses_cleaned, simulated_df], ignore_index=True)
original_data['responses'] = combined_responses

# Helper: simulate Poisson-based edges
def simulate_poisson_edges(existing_df, new_ids, all_ids, lambda_estimate):
    edges = []
    for source_id in new_ids:
        num_targets = np.random.poisson(lambda_estimate)
        num_targets = min(max(num_targets, 1), len(all_ids)-1)
        targets = np.random.choice([t for t in all_ids if t != source_id], size=num_targets, replace=False)
        for target in targets:
            edges.append({'Source': source_id, 'Target': target})
    return pd.concat([existing_df, pd.DataFrame(edges)], ignore_index=True)

# Update networks
all_ids = combined_responses['Participant-ID'].tolist()
network_sheets = [
    'net_0_Friends', 'net_1_Influential', 'net_2_Feedback',
    'net_3_MoreTime', 'net_4_Advice', 'net_5_Disrespect'
]
for sheet in network_sheets:
    existing_df = original_data[sheet]
    lambda_estimate = existing_df['Source'].value_counts().mean()
    updated_df = simulate_poisson_edges(existing_df, new_ids, all_ids, lambda_estimate)
    original_data[sheet] = updated_df

# Update affiliation network
affiliations_df = original_data['affiliations']
affiliation_ids = affiliations_df['ID'].dropna().unique()
affil_edges = []
for source_id in new_ids:
    n_affils = np.random.poisson(2)
    n_affils = max(1, min(n_affils, len(affiliation_ids)))
    assigned = np.random.choice(affiliation_ids, size=n_affils, replace=False)
    for affil in assigned:
        affil_edges.append({'Source': source_id, 'Target': affil})
original_data['net_affiliation_0_SchoolActivit'] = pd.concat([
    original_data['net_affiliation_0_SchoolActivit'],
    pd.DataFrame(affil_edges)
], ignore_index=True)

# ✅ Update participants sheet
participants_df = original_data['participants']
participant_columns = participants_df.columns.tolist()
participant_columns.remove('Participant-ID')

new_participants = []
for pid in new_ids:
    row = {'Participant-ID': pid}
    for col in participant_columns:
        values = participants_df[col].dropna().unique()
        row[col] = np.random.choice(values) if len(values) > 0 else None
    new_participants.append(row)

new_participants_df = pd.DataFrame(new_participants)
updated_participants_df = pd.concat([participants_df, new_participants_df], ignore_index=True)
original_data['participants'] = updated_participants_df

# ✅ Save full updated workbook
final_path = "../SchoolData/Student_Survey_AllSheets_Updated.xlsx"
with pd.ExcelWriter(final_path, engine='xlsxwriter') as writer:
    for name, df in original_data.items():
        df.to_excel(writer, sheet_name=name[:31], index=False)

print("Saved to:", final_path)
