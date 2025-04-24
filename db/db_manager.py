from database import Database

# Get the singleton instance and connect
def get_db():
    db = Database(config_file='./config.json')
    db.connect()
    return db

def close_db():
    db = Database()
    db.close_connection()
