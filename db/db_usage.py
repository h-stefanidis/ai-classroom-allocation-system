from db.db_manager import get_db

db = get_db()
results = db.fetch_all("""SELECT participant_id, perc_academic, perc_effort, attendance FROM raw.participants""")
print(results)
