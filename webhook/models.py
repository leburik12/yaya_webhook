from django.db import models

# Create your models here.

# {
#     "id": "1dd2854e-3a79-4548-ae36-97e4a18ebf81",
#     "amount": 100,
#     "currency": "ETB",
#     "created_at_time": 1673381836,
#     "timestamp": 1701272333,
#     "cause": "Testing",
#     "full_name": "Abebe Kebede",
#     "account_name": "abebekebede1",
#     "invoice_url": "https://yayawallet.com/en/invoice/xxxx",
# }


class WebhookEvent(models.Model):
    id = models.CharField(max_length=255, unique=True, primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    created_at_time = models.BigIntegerField()
    timestamp = models.BigIntegerField()
    cause = models.TextField()
    full_name = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255)
    invoice_url = models.URLField()
    received_at = models.DateTimeField(auto_now_add=True)
