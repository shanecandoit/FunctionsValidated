from sqlmodel import Session, create_engine
from pathlib import Path

# Create database URL
sqlite_file = Path("schema_process.db")
sqlite_url = f"sqlite:///{sqlite_file.absolute()}"

# Create engine
engine = create_engine(sqlite_url, echo=True)

# Dependency for database session
def get_session():
    with Session(engine) as session:
        yield session
