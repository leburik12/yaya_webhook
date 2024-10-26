from django.test import TestCase
import json
import time
import hmac
import hashlib
from django.urls import reverse
from django.conf import settings

# Create your tests here.


class WebhookViewTestCase(TestCase):
    def setUp(self):
        # secret key for testing
        self.secret_key = "test_secret_key"

        # payload and create expected signed payload for signature
        self.payload = {
            "id": "1dd2854e-3a79-4548-ae36-97e4a18ebf81",
            "amount": 100,
            "currency": "ETB",
            "created_at_time": 1673381836,
            "timestamp": int(time.time()),  # Current timestamp
            "cause": "Testing",
            "full_name": "Abebe Kebede",
            "account_name": "abebekebede1",
            "invoice_url": "https://yayawallet.com/en/invoice/xxxx",
        }

        # signed payload (concatenate payload values as string)
        signed_payload = "".join([str(self.payload.get(k)) for k in self.payload])

        # expected HMAC SHA256 signature using the secret key
        self.expected_signature = hmac.new(
            self.secret_key.encode(), signed_payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        #  headers including the YAYA-SIGNATURE with expected signature
        self.headers = {
            "HTTP_YAYA_SIGNATURE": self.expected_signature  # Django test client requires headers with HTTP_ prefix
        }

    def test_webhook_valid_signature(self):
        """
        Test webhook endpoint with a valid signature and valid timestamp.
        """
        response = self.client.post(
            reverse("webhook-endpoint"),  # view rather that hardcoded url
            data=json.dumps(self.payload),
            content_type="application/json",
            **self.headers
        )

        # Assert the response status code is 200
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("status"), "success")

    def test_webhook_invalid_signature(self):
        """
        Test webhook endpoint with an invalid signature.
        """

        # Modify the signature to make it invalid
        self.headers["HTTP_YAYA_SIGNATURE"] = "invalid_signature"

        response = self.client.post(
            reverse("webhook-endpoint"),
            data=json.dumps(self.payload),
            content_type="application/json",
            **self.headers
        )

        # Assert the response status code is 403
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get("error"), "Invalid signature")

    def test_webhook_timestamp_tolerance(self):
        """
        Test webhook endpoint with a timestamp outside the tolerance window.
        """
        # Modify the payload timestamp to be outside the allowed value
        self.payload["timestamp"] = int(time.time()) - (
            settings.TIME_TOLERANCE_SECONDS + 1
        )

        # Recreate the signed payload and signature
        signed_payload = "".join([str(self.payload.get(k)) for k in self.payload])
        self.headers["HTTP_YAYA_SIGNATURE"] = hmac.new(
            self.secret_key.encode(), signed_payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        response = self.client.post(
            reverse("webhook-endpoint"),
            data=json.dumps(self.payload),
            content_type="application/json",
            **self.headers
        )

        # Assert the response status code is 408, indicating request timeout
        self.assertEqual(response.status_code, 408)
        self.assertEqual(
            response.json().get("error"), "Request timestamp out of tolerance"
        )
