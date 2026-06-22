from auth.totp import generate_totp_secret, generate_qr_code
from db.database import get_connection


def enable_2fa_for_user(username):
    secret = generate_totp_secret()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE users
        SET totp_secret = %s, is_2fa_enabled = TRUE
        WHERE username = %s;
        """,
        (secret, username)
    )
    conn.commit()
    cur.close()
    conn.close()

    qr_path = generate_qr_code(username, secret)
    print(f"2FA enabled for '{username}'.")
    print(f"QR code saved at: {qr_path}")
    print("Scan this with Google Authenticator!")


if __name__ == "__main__":
    enable_2fa_for_user("willis")