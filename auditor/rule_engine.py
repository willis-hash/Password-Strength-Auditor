import re


def estimate_crack_time(password, has_upper, has_lower, has_digit, has_special):
    """
    Estimate crack time based on character set size and password length.
    Assumes 1 billion guesses per second (modern CPU offline attack).
    """
    charset_size = 0
    if has_lower:
        charset_size += 26
    if has_upper:
        charset_size += 26
    if has_digit:
        charset_size += 10
    if has_special:
        charset_size += 32

    if charset_size == 0:
        charset_size = 10

    combinations = charset_size ** len(password)
    guesses_per_second = 1_000_000_000  # 1 billion/sec (CPU offline)
    seconds = combinations / guesses_per_second

    if seconds < 1:
        return "Instantly"
    elif seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hours"
    elif seconds < 31536000:
        return f"{int(seconds // 86400)} days"
    elif seconds < 3153600000:
        return f"{int(seconds // 31536000)} years"
    else:
        return "Centuries"


def evaluate_password(password):
    """
    Evaluate a password against compositional rules.
    Returns a dict with score, label, issues, and crack time.
    """
    issues = []
    score = 0

    # 1. Length check
    if len(password) < 8:
        issues.append("Password is too short (minimum 8 characters).")
    elif len(password) >= 16:
        score += 2
    else:
        score += 1

    # 2. Character composition
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[^A-Za-z0-9]", password))

    composition_count = sum([has_upper, has_lower, has_digit, has_special])
    score += composition_count

    if not has_upper:
        issues.append("Missing uppercase letters.")
    if not has_lower:
        issues.append("Missing lowercase letters.")
    if not has_digit:
        issues.append("Missing numeric digits.")
    if not has_special:
        issues.append("Missing special characters.")

    # 3. Predictable pattern detection
    common_patterns = [
        r"1234", r"qwerty", r"asdf", r"password", r"letmein",
        r"abc123", r"admin", r"welcome"
    ]
    lowered = password.lower()
    for pattern in common_patterns:
        if pattern in lowered:
            issues.append(f"Contains a predictable pattern: '{pattern}'.")
            score -= 2
            break

    # 4. Repeated/sequential characters
    if re.search(r"(.)\1{2,}", password):
        issues.append("Contains repeated characters (e.g. 'aaa').")
        score -= 1

    if re.search(r"(0123|1234|2345|3456|4567|5678|6789|9876|8765|7654|6543|5432|4321|3210)", password):
        issues.append("Contains sequential numbers.")
        score -= 1

    # Clamp score
    score = max(0, score)

    # Determine label
    if score <= 2:
        label = "Weak"
    elif score <= 4:
        label = "Moderate"
    else:
        label = "Strong"

    # Crack time estimate
    crack_time = estimate_crack_time(password, has_upper, has_lower, has_digit, has_special)

    return {
        "score": score,
        "label": label,
        "issues": issues,
        "crack_time": crack_time,
        "has_upper": has_upper,
        "has_lower": has_lower,
        "has_digit": has_digit,
        "has_special": has_special,
    }