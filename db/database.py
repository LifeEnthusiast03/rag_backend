
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URI = "postgresql://postgres:password@localhost:5432/rag_database"
engine = create_engine(DATABASE_URI)
sessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
