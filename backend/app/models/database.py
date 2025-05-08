#import psycopg2
#from sqlalchemy import create_engine
#from app.models.db_models import Base
#from config import Config



## Create the 'easyresi' database if it doesn't exist
#def create_database():
#    try:
#        connection = psycopg2.connect(user=Config.DB_USER, password=Config.DB_PASSWORD, host=Config.DB_HOST, port=Config.DB_PORT)
#        connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
#        cursor = connection.cursor()

#        # Check if the database exists
#        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{Config.DB_NAME}'")
#        exists = cursor.fetchone()
        
#        if not exists:
#            cursor.execute(f'CREATE DATABASE {Config.DB_NAME}')
#            print(f"Database '{Config.DB_NAME}' created successfully")
#        else:
#            print(f"Database '{Config.DB_NAME}' already exists")
    
#        cursor.close()
#        connection.close()
#    except Exception as e:
#        print(f"Error creating database: {e}")


## Create tables in the 'easyresi' database
#def create_tables():
#    try:
#        # Recreate the engine, now the database should exist
#        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
#        Base.metadata.create_all(engine)
#        print("All tables created successfully")
#    except Exception as e:
#        print(f"Error creating tables: {e}")
