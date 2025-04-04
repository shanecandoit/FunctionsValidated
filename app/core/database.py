from sqlmodel import Session, create_engine
from pathlib import Path

# Create database URL
sqlite_file = Path("schema_process.db")
sqlite_url = f"sqlite:///{sqlite_file.absolute()}"

# Create engine
# Add connect_args to allow SQLite usage across threads (common requirement for async frameworks)
engine = create_engine(sqlite_url, echo=True, connect_args={"check_same_thread": False})

# Dependency for database session
def get_session():
    with Session(engine) as session:
        yield session
