from auditor.rule_engine import evaluate_password
from auditor.jtr_integration import crack_with_jtr


def full_audit(password):
    """
    Run the complete password audit pipeline:
    1. Rule-based analysis
    2. JtR dictionary attack simulation
    3. Reconcile into final classification
    """
    rule_result = evaluate_password(password)
    jtr_result = crack_with_jtr(password, hash_type="md5")

    final_label = rule_result["label"]
    recommendations = list(rule_result["issues"])

    if jtr_result["cracked"]:
        final_label = "Vulnerable"
        recommendations.insert(
            0,
            "This password was successfully cracked using a dictionary attack. "
            "It is present in a known breached password wordlist."
        )

    if not recommendations:
        recommendations.append("No issues detected. This is a strong password.")

    return {
        "password_length": len(password),
        "rule_score": rule_result["score"],
        "rule_label": rule_result["label"],
        "cracked_by_jtr": jtr_result["cracked"],
        "final_label": final_label,
        "recommendations": recommendations,
    }


if __name__ == "__main__":
    test_passwords = ["123456", "Password1", "Tr0ub4dor&3", "X7$qP9!zR2#vL5mK"]
    for pw in test_passwords:
        print(f"\n{'='*50}")
        print(f"Auditing: {pw}")
        result = full_audit(pw)
        for key, value in result.items():
            print(f"{key}: {value}")