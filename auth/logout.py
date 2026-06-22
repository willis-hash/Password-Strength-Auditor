import uuid
from datetime import datetime, timedelta
from db.database import get_connection
from config import SESSION_EXPIRY_HOURS


def create_session(user_id):
    """Create a new session for a logged-in user."""
    conn = get_connection()
    if not conn:
        return None

    try:
        token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=SESSION_EXPIRY_HOURS)

        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO sessions (user_id, session_token, expires_at, is_active)
            VALUES (%s, %s, %s, TRUE)
            RETURNING id;
            """,
            (user_id, token, expires_at)
        )
        session_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return {"session_id": session_id, "token": token, "expires_at": expires_at}
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"Failed to create session: {e}")
        return None


def logout_session(session_token):
    """Invalidate a session (logout)."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE sessions
            SET is_active = FALSE
            WHERE session_token = %s;
            """,
            (session_token,)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"Failed to logout: {e}")
        return False


def is_session_valid(session_token):
    """Check if a session token is still active and not expired."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT is_active, expires_at FROM sessions
            WHERE session_token = %s;
            """,
            (session_token,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return False

        is_active, expires_at = row
        return is_active and expires_at > datetime.now()
    except Exception as e:
        conn.close()
        print(f"Failed to validate session: {e}")
        return False


if __name__ == "__main__":
    # Quick manual test using user_id=1 (willis from login.py test)
    session = create_session(1)
    print("Session created:", session)

    valid = is_session_valid(session["token"])
    print("Session valid?", valid)

    logout_session(session["token"])
    valid_after_logout = is_session_valid(session["token"])
    print("Session valid after logout?", valid_after_logout)