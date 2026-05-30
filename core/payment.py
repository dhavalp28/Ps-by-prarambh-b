import hashlib
import hmac
import os

import razorpay


class RazorpayClient:
    def __init__(self):
        self.key_id = os.getenv("RAZORPAY_KEY_ID", "")
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
        self.client = razorpay.Client(auth=(self.key_id, self.key_secret))

    def is_configured(self) -> bool:
        return bool(self.key_id and self.key_secret)

    def create_order(
        self,
        *,
        amount_subunits: int,
        currency: str,
        receipt: str,
        notes: dict | None = None,
    ):
        return self.client.order.create(
            data={
                "amount": amount_subunits,
                "currency": currency,
                "receipt": receipt,
                "notes": notes or {},
            }
        )

    def verify_signature(
        self, *, order_id: str, payment_id: str, signature: str
    ) -> bool:
        generated = hmac.new(
            self.key_secret.encode(),
            f"{order_id}|{payment_id}".encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(generated, signature)


razorpay_client = RazorpayClient()
