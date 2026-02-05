from .database import sessionLocal

def init_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()