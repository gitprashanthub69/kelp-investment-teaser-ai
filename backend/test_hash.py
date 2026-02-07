from passlib.context import CryptContext
import sys

try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    pass_hash = pwd_context.hash("testpassword")
    print(f"Hash success: {pass_hash}")
    verify = pwd_context.verify("testpassword", pass_hash)
    print(f"Verify success: {verify}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
