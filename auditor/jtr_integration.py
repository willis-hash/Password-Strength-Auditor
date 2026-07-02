import hashlib
import subprocess
import tempfile
import os
import re
from config import JOHN_PATH, WORDLIST_PATH


def hash_password(password):
    """Generate MD5 and SHA-1 hashes of a password."""
    md5_hash = hashlib.md5(password.encode("utf-8")).hexdigest()
    sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest()
    return {"md5": md5_hash, "sha1": sha1_hash}


def crack_with_jtr(password, hash_type="md5", use_rules=False, timeout=30):
    """
    Attempt to crack a password's hash using John the Ripper.
    Writes the hash to a temp file in JtR's expected format,
    runs JtR via subprocess, and parses whether it was cracked.

    Returns dict: {"cracked": bool, "method": str, "crack_time": float or None}
    """
    hashes = hash_password(password)
    target_hash = hashes[hash_type]

    # Create a temp file with username:hash format
    fd, hash_file_path = tempfile.mkstemp(suffix=".txt")
    try:
        with os.fdopen(fd, "w") as f:
            # JtR raw hash format
            f.write(f"testuser:{target_hash}\n")

        format_map = {"md5": "raw-md5", "sha1": "raw-sha1"}
        jtr_format = format_map.get(hash_type, "raw-md5")

        cmd = [
            JOHN_PATH,
            f"--format={jtr_format}",
            f"--wordlist={WORDLIST_PATH}",
        ]

        if use_rules:
            cmd.append("--rules")

        cmd.append(hash_file_path)

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            return {"cracked": False, "method": "timeout", "output": "JtR timed out."}

        # Check results using --show
        show_cmd = [JOHN_PATH, f"--format={jtr_format}", "--show", hash_file_path]
        show_result = subprocess.run(show_cmd, capture_output=True, text=True)

        cracked = "testuser:" in show_result.stdout and not show_result.stdout.strip().endswith("0 password hash cracked")

        # More reliable check: look for "1 password hash cracked" in show output footer
        match = re.search(r"(\d+) password hash(es)? cracked", show_result.stdout)
        cracked_count = int(match.group(1)) if match else 0

        # Extract crack time from JtR output e.g. "0:00:00:01"
        import re as _re
        time_match = _re.search(r"(\d+:\d+:\d+:\d+)", result.stdout)
        crack_time = time_match.group(1) if time_match else None

        return {
        "cracked": cracked_count > 0,
        "method": "rules" if use_rules else "dictionary",
        "crack_time": crack_time,
        "raw_output": result.stdout,
        "show_output": show_result.stdout,
        }

    finally:
        if os.path.exists(hash_file_path):
            os.remove(hash_file_path)
        # Clean up JtR's pot file entry isn't strictly necessary for this use case


if __name__ == "__main__":
    # Test with a known weak password (should be in rockyou.txt)
    print("Testing weak password '123456'...")
    result = crack_with_jtr("123456", hash_type="md5")
    print(result)

    print("\nTesting strong password 'X7$qP9!zR2#vL5mK'...")
    result2 = crack_with_jtr("X7$qP9!zR2#vL5mK", hash_type="md5")
    print(result2)