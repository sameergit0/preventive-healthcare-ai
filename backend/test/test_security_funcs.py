from app.core import hash_password, verify_password, create_access_token
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

AK_SECRET_KEY = os.getenv("AK_SECRET_KEY")
AK_ALGORITHM = os.getenv("AK_ALGORITHM")

# passwrod = "abc123@sam"

# result = hash_password(plain_password=passwrod)

# verify = verify_password(plain_password="abc123@sam", hashed_password=result)
# print(result)
# print(verify)

email = "sameer@gmail.com"

data={"sub": email}

token = create_access_token(data=data)

payload = jwt.decode(token, AK_SECRET_KEY, algorithms=[AK_ALGORITHM])
print(token)
print(payload)