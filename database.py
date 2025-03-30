from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://u76mpdnh0jcs1l:p34ba1b6e661cab3bc19b27221ecd7141ffdef13bf7491a1ce2903058c86f253d@c4c161t4pf58h3.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/da1c5m8j3raf81"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()