from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URI = os.getenv("DATABASE_URI")
if not DATABASE_URI:
    raise ValueError("DATABASE_URI is not set. If running locally, check your .env file. If using Docker, ensure docker-compose passes it or set it in the environment.")

engine = create_engine(DATABASE_URI)
sessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
