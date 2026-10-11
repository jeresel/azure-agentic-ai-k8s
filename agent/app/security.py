import re

SENSITIVE_PATTERNS = [
    # Authorization bearer tokens
    (
        re.compile(
            r"(?i)(Bearer\s+)[A-Za-z0-9._~+/-]+"
        ),
        r"\1[REDACTED]",
    ),

    # Common key/value secrets in logs
    (
        re.compile(
            r"""(?i)(["']?(?:password|passwd|secret|api_key|apikey|access_token|refresh_token|client_secret)["']?\s*[:=]\s*)("[^"]*"|'[^']*'|[^\s,}\]]+)"""
        ),
        r"\1[REDACTED]",
    ),

    # Azure Storage connection string account keys
    (
        re.compile(
            r"(?i)(AccountKey=)[^;\s]+"
        ),
        r"\1[REDACTED]",
    ),
]


def redact_sensitive_data(text: str) -> str:
    """Redact common credentials before sending data to an LLM."""
    for pattern, replacement in SENSITIVE_PATTERNS:
        text = pattern.sub(replacement, text)

    return text
