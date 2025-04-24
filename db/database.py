import psycopg2
from psycopg2 import OperationalError, Error
import json
import pandas as pd
import logging
from threading import Lock
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    _instance = None
    _lock = Lock()

    def __new__(cls, config_file='config.json'):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_file='config.json'):
        if self._initialized:
            return
        self.config = self.load_config(config_file)
        self.connection = None
        self._initialized = True

    def load_config(self, config_file):
        # Always load the config file relative to the location of database.py
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, config_file)
        try:
            with open(config_path, 'r') as file:
                config = json.load(file)
            return config['database']
        except FileNotFoundError as e:
            print(f"ERROR:database:Error loading config: {e}")
            raise

    def connect(self):
        if self.connection is None:
            try:
                self.connection = psycopg2.connect(
                    user=self.config['user'],
                    password=self.config['password'],
                    host=self.config['host'],
                    port=self.config['port'],
                    dbname=self.config['dbname']
                )
                logger.info("Connected to PostgreSQL database.")
            except OperationalError as e:
                logger.error(f"Database connection failed: {e}")
                self.connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    ### execute_query is strictly useds for operations like INSERT, UPDATE, DELETE, creating tables, etc. Not for SELECT.    
    def execute_query(self, query, data=None):
        if not self.connection:
            logger.warning("No database connection.")
            return None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, data)
                self.connection.commit()
                logger.info("Query executed.")
        except Error as e:
            logger.error(f"Query execution failed: {e}")

    def fetch_all(self, query, data=None):
        if not self.connection:
            logger.warning("No database connection.")
            return None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, data)
                return cursor.fetchall()
        except Error as e:
            logger.error(f"Fetch failed: {e}")
            return None

    def execute_many(self, query, data):
        if not self.connection:
            logger.warning("No database connection.")
            return None
        try:
            with self.connection.cursor() as cursor:
                cursor.executemany(query, data)
                self.connection.commit()
                logger.info("Bulk insert executed.")
        except Error as e:
            logger.error(f"Bulk insert failed: {e}")

    def query_df(self, query, data=None):
        if not self.connection:
            logger.warning("No database connection.")
            return None
        try:
            return pd.read_sql_query(query, self.connection, params=data)
        except Error as e:
            logger.error(f"DataFrame query failed: {e}")
            return None

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed.")
