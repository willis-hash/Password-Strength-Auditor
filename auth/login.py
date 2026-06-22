import bcrypt
from db.database import get_connection


def hash_password(plain_password):
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password, hashed_password):
    """Check a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def register_user(username, email, plain_password):
    """Insert a new user into the database with a hashed password."""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        hashed = hash_password(plain_password)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (username, email, hashed)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return True, user_id
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)


def authenticate_user(username, plain_password):
    """
    Check username + password against the database.
    Returns (success, user_dict_or_error_message).
    """
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, username, email, password_hash,
                   totp_secret, is_2fa_enabled
            FROM users WHERE username = %s;
            """,
            (username,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return False, "User not found."

        user = {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "password_hash": row[3],
            "totp_secret": row[4],
            "is_2fa_enabled": row[5],
        }

        if not verify_password(plain_password, user["password_hash"]):
            return False, "Incorrect password."

        return True, user

    except Exception as e:
        conn.close()
        return False, str(e)


if __name__ == "__main__":
    # Quick manual test
    success, result = register_user("willis", "willis@example.com", "TestPass123!")
    print("Register:", success, result)

    success, result = authenticate_user("willis", "TestPass123!")
    print("Login:", success, result)