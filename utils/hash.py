from bcrypt import checkpw, hashpw, gensalt

def hash_password(password: str) -> str:
    """This function generates the hash for the password"""
    salt = gensalt(10)
    hashed_password = hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """This function verifies the hashed password"""
    try:
        return checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        print(f"Password verification error: {e}")
        return False