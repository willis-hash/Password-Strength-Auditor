import re


def evaluate_password(password):
    """
    Evaluate a password against compositional rules.
    Returns a dict with score, label, and list of issues.
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
        issues.append("Contains repeated characters (e.g., 'aaa').")
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

    return {
        "score": score,
        "label": label,
        "issues": issues,
        "has_upper": has_upper,
        "has_lower": has_lower,
        "has_digit": has_digit,
        "has_special": has_special,
    }


if __name__ == "__main__":
    test_passwords = ["123456", "Password1", "Tr0ub4dor&3", "MyV3ryStr0ng!Passw0rd2026"]
    for pw in test_passwords:
        result = evaluate_password(pw)
        print(f"\nPassword: {pw}")
        print(f"Score: {result['score']} | Label: {result['label']}")
        for issue in result['issues']:
            print(f"  - {issue}")