from sqlalchemy import text
from app.db import sessionLocal

def test_connection():
    db = sessionLocal()
    
    try:
        result = db.execute(text("SELECT 1"))
        print(f"✅ Success! Database returned: {result.scalar()}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        db.close()
        
if __name__ == "__main__":
    test_connection()