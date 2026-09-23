import bcrypt



def hash_secret(plain: str) -> str:
    secret = plain.encode("utf-8")
    if len(secret) > 72:
        raise ValueError("Secret cannot be longer than 72 UTF-8 bytes")
    return bcrypt.hashpw(secret, bcrypt.gensalt()).decode("ascii")


def verify_secret(plain: str, hashed: str) -> bool:
    secret = plain.encode("utf-8")
    if len(secret) > 72:
        return False
    try:
        return bcrypt.checkpw(secret, hashed.encode("ascii"))
    except ValueError:
        return False
