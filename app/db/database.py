from sqlalchemy import create_engine                #Decides the type of the database to be used
from sqlalchemy.orm import declarative_base, sessionmaker               #declarative_base() is used to map the database tables to Python classes
                                                                        #sessionmaker() is used to create a session factory for interacting with the database
import os

DB_DIR = "data"
os.makedirs(DB_DIR, exist_ok=True)
SQL_DATABASE_URL = f"sqlite:///{DB_DIR}/customer_support.db"

engine = create_engine(SQL_DATABASE_URL, connect_args={"check_same_thread": False})  #Allows multiple threads to access the same SQLite database file concurrently
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()