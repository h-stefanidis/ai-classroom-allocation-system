from db.db_manager import get_db
import pandas as pd
# Extended sheet to table mapping (including all schema entries)
sheet_table_map = {
    "participants": "participants",
    "responses": "responses",
    "affiliations": "affiliations",
    "net_0_Friends": "friends",
    "net_1_Influential": "influential",
    "net_2_Feedback": "feedback",
    "net_3_MoreTime": "more_time",
    "net_4_Advice": "advice",
    "net_5_Disrespect": "disrespect",
    "net_affiliation_0_SchoolActivit": "net_affiliation_0_school_activity"
}

# Column renaming maps
column_renames = {
    "participants": {
        "Participant-ID": "participant_id",
        "Type": "type",
        "First-Name": "first_name",
        "Last-Name": "last_name",
        "Email": "email",
        "Contact Number": "contact_number",
        "Perc_Effort": "perc_effort",
        "Attendance": "attendance",
        "Perc_Academic": "perc_academic",
        "CompleteYears": "complete_years",
        "House": "house"
    },
    "responses": {
        "survey-instance-id": "survey_instance_id",
        "Participant-ID": "participant_id",
        "Status": "status",
        "Manbox5_1": "manbox5_1",
        "Manbox5_2": "manbox5_2",
        "Manbox5_3": "manbox5_3",
        "Manbox5_4": "manbox5_4",
        "Manbox5_5": "manbox5_5",
        "isolated": "isolated",
        "WomenDifferent": "women_different",
        "Manbox5_overall": "manbox5_overall",
        "language": "language",
        "Masculinity_contrained": "masculinity_contrained",
        "GrowthMindset": "growth_mindset",
        "COVID": "covid",
        "criticises": "criticises",
        "MenBetterSTEM": "men_better_stem",
        "School_support_engage6": "school_support_engage6",
        "pwi_wellbeing": "pwi_wellbeing",
        "Intelligence1": "intelligence1",
        "Intelligence2": "intelligence2",
        "Soft": "soft",
        "opinion": "opinion",
        "Nerds": "nerds",
        "School_support_engage": "school_support_engage",
        "comfortable": "comfortable",
        "future": "future",
        "bullying": "bullying",
        "candidate_Perc_Effort": "candidate_perc_effort"
    },
    "affiliations": {
        "ID": "id",
        "Title": "title",
        "Category": "category",
        "Description": "description",
        "nominationWave": "nominationwave",
        "addtional info 2": "additional_info_2",
        "additonal info 1": "additional_info_1"
    },
}

# Standard edge list column names
edge_columns = ["id", "source", "target"]


def insert_excel_data_to_db(excel_path, cohort_value):
    db = get_db()
    conn = db.connection  # Get the raw psycopg2 connection

    try:
        with conn:
            with conn.cursor() as cursor:
                with pd.ExcelFile(excel_path) as xls:
                    for sheet_name, table_name in sheet_table_map.items():
                        print(f"Processing: {sheet_name} → {table_name}")
                        df = xls.parse(sheet_name)
                        df.columns = df.columns.str.strip()

                        if sheet_name in column_renames:
                            df.rename(columns=column_renames[sheet_name], inplace=True)
                        elif sheet_name.startswith("net_") or table_name in ["advice", "feedback", "disrespect", "influential", "friends", "more_time", "net_affiliation_0_school_activity"]:
                            if len(df.columns) == 2:
                                df.columns = ["source", "target"]
                            elif len(df.columns) == 3:
                                df.columns = ["id", "source", "target"]

                        if table_name == "participants":
                            df["cohort"] = cohort_value

                        df.dropna(how="all", inplace=True)
                        df.columns = [col.lower() for col in df.columns]

                        if df.empty:
                            print(f"Skipped {sheet_name} — no data")
                            continue

                        columns = list(df.columns)
                        data = [tuple(map(lambda x: x.item() if hasattr(x, 'item') else x, row)) for row in df.to_numpy()]
                        placeholders = ", ".join(["%s"] * len(columns))
                        col_str = ", ".join(columns)
                        query = f"INSERT INTO raw.{table_name} ({col_str}) VALUES ({placeholders});"

                        cursor.executemany(query, data)
                        print(f"Inserted {len(data)} rows into '{table_name}'")
        return True

    except Exception as e:
        print(f"Failed to import entire file: {e}")
        return False