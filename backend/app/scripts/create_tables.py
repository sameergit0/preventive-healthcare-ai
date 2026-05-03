from app import base_models
from app.db import Base, engine

print("Creating tables...")

Base.metadata.create_all(bind=engine)

print("Tables created!")