import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv('DB_ADDRESS'))
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
