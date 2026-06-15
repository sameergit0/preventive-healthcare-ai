import pandas as pd

from app.db import sessionLocal
from app.models import Profile

# Initialize database session
db = sessionLocal()

try:
    # Fetch all profiles
    profiles = db.query(Profile).all()

    # Create a list of dictionaries using actual database column names
    profiles_data = []
    for p in profiles:
        profiles_data.append({
            "user_id": p.user_id,
            "age": p.age,
            "gender": p.gender,
            "weight_kg": p.weight,
            "height_cm": p.height,
            "waist_cm": p.waist_cm
        })
        
    profiles_df = pd.DataFrame(profiles_data)
    profiles_df.head()
    
    db.close()
    print("\nDatabase connection closed.")
    
    print("--- Profiles Dataframe (First 5 Rows with Actual DB Columns) ---")
    print(profiles_df.head(5))

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    db.close()
    print("\nDatabase connection closed.")

