from app.database import SessionLocal


def lay_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
