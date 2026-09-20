import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load .env file from backend/.env or root .env
env_path = find_dotenv("backend/.env") or find_dotenv(".env")
if env_path:
    load_dotenv(env_path)
else:
    load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:NewPassword123!@127.0.0.1:3306/college_management_system"
)

# Connect to database using pool_pre_ping for MySQL connection health checks
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
