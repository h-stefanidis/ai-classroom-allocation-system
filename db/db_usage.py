from db_manager import get_db

db = get_db()
results = db.fetch_all("SELECT * FROM raw.participants limit 5;")
print(results)
