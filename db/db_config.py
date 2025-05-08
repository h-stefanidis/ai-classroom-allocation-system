import json
from pathlib import Path

# def load_db_url(config_path=None):
#     if config_path is None:
#         config_path = Path(__file__).resolve().parent / "config.json"
#     with open(config_path, "r") as f:
#         config = json.load(f)["database"]

#     user = config["user"]
#     password = config["password"]
#     host = config["host"]
#     port = config["port"]
#     dbname = config["dbname"]

#     return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


def load_db_url(config_path="config.json"):
    with open(config_path, "r") as f:
        config = json.load(f)["database"]
    user = config["user"]
    password = config["password"]
    host = config["host"]
    port = config["port"]
    dbname = config["dbname"]
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
