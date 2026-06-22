import pyotp
import qrcode
import os


def generate_totp_secret():
    """Generate a new random TOTP secret for a user."""
    return pyotp.random_base32()


def generate_qr_code(username, secret, app_name="PasswordAuditor"):
    """
    Generate a QR code image for the user to scan with
    Google Authenticator / Authy. Saves it to assets/qr_codes/.
    """
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=username, issuer_name=app_name)

    qr_dir = os.path.join("assets", "qr_codes")
    os.makedirs(qr_dir, exist_ok=True)

    qr_path = os.path.join(qr_dir, f"{username}_qr.png")
    img = qrcode.make(uri)
    img.save(qr_path)

    return qr_path


def verify_totp_code(secret, code):
    """Verify a 6-digit TOTP code against the stored secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


if __name__ == "__main__":
    # Quick test
    secret = generate_totp_secret()
    print("Generated secret:", secret)
    path = generate_qr_code("test_user", secret)
    print("QR code saved at:", path)
    code = input("Enter the code from your authenticator app: ")
    print("Valid?", verify_totp_code(secret, code))