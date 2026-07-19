"""Password hashing: PBKDF2-HMAC-SHA256 with a per-user random salt.

Not bcrypt/argon2 - stdlib hashlib+secrets get the same core property (slow,
salted, no rainbow-table reuse) without adding a new dependency, consistent
with this project's minimal-dependency stance. bcrypt/argon2 remain strictly
better if this were ever to leave course-project scope.
"""

import hashlib
import hmac
import secrets

_ITERATIONS = 200_000


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """Return (hash_hex, salt_hex). Generates a fresh random salt if none is
    given (the normal case, when hashing a new password); pass an existing
    salt back in to recompute the same hash for verification."""
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), _ITERATIONS)
    return digest.hex(), salt


def verify_password(password: str, expected_hash: str, salt: str) -> bool:
    """Constant-time comparison (hmac.compare_digest) so a failed check
    can't leak timing information about how much of the hash matched."""
    actual_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(actual_hash, expected_hash)
