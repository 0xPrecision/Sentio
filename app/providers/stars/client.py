from __future__ import annotations
import hmac, hashlib

class StarsClient:
    """Seam for Telegram Stars signature verification and API calls.

    TODO(api): confirm exact header and HMAC scheme.
    """
    def __init__(self, webhook_secret: str):
        self.secret = webhook_secret.encode()

    def verify_signature(self, signature_header: str, body: bytes) -> bool:
        mac = hmac.new(self.secret, body, hashlib.sha256).hexdigest()
        try:
            provided = signature_header.split("=")[-1]
        except Exception:
            return False
        return hmac.compare_digest(mac, provided)
