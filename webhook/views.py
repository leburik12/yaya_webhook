from django.shortcuts import render

# Create your views here.
import json
import hmac
import hashlib
import time
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import WebhookEvent

# Load the webhook secret from environment variables or settings
WEBHOOK_SECRET = settings.WEBHOOK_SECRET

# @csrf_exempt
# def yaya_webhook(request):
#     if request.method == 'POST':
#         try:
#             payload = json.loads(request.body)
#             received_signature = request.headers.get("YAYA-SIGNATURE", "")
#             timestamp = payload.get("timestamp", 0)

#             expected_signature = generate_signature(payload, WEBHOOK_SECRET)
#             time_difference = abs(time.time() - timestamp)

#             if hmac.compare_digest(received_signature, expected_signature) and time_difference <= 300:
#                 WebhookEvent.objects.create(
#                     event_id=payload['id'],
#                     amount=payload['amount'],
#                     currency=payload['currency'],
#                     created_at_time=payload['created_at_time'],
#                     timestamp=payload['timestamp'],
#                     cause=payload['cause'],
#                     full_name=payload['full_name'],
#                     account_name=payload['account_name'],
#                     invoice_url=payload['invoice_url'],
#                 )
#                 return JsonResponse({'status': 'success'}, status=200)
#             else:
#                 return JsonResponse({'error': 'Invalid signature or request timeout'}, status=400)

#         except (json.JSONDecodeError, KeyError) as e:
#             return JsonResponse({'error': f'Invalid request: {str(e)}'}, status=400)

#     return JsonResponse({'error': 'Method not allowed'}, status=405)


# Set the time tolerance in seconds (5 minutes)
TIME_TOLERANCE_SECONDS = getattr(settings, "TIME_TOLERANCE_SECONDS", 300)


@csrf_exempt
def yaya_webhook(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    # Extract payload and headers
    try:
        payload = request.json()  # Assuming JSON body
        received_signature = request.headers.get("YAYA-SIGNATURE", "")
        payload_timestamp = payload.get("timestamp", 0)  # In seconds since epoch
    except ValueError:
        return JsonResponse({"error": "Invalid payload"}, status=400)

    # Step 1: Check the time difference
    current_time = int(time.time())
    time_difference = abs(current_time - int(payload_timestamp))

    if time_difference > TIME_TOLERANCE_SECONDS:
        return JsonResponse({"error": "Request timestamp too old"}, status=400)

    # Step 2: Generate the expected signature
    secret_key = settings.YAYA_SECRET_KEY
    expected_signature = generate_signature(payload, secret_key)

    # Step 3: Verify the signature
    if not hmac.compare_digest(received_signature, expected_signature):
        return JsonResponse({"error": "Invalid signature"}, status=403)

    # Step 4: Save the payload to the database
    try:
        WebhookEvent.objects.create(
            id=payload.get("id"),
            amount=payload.get("amount"),
            currency=payload.get("currency"),
            created_at_time=payload.get("created_at_time"),
            timestamp=payload_timestamp,
            cause=payload.get("cause"),
            full_name=payload.get("full_name"),
            account_name=payload.get("account_name"),
            invoice_url=payload.get("invoice_url"),
        )
    except Exception as e:
        return JsonResponse({"error": f"Database error: {str(e)}"}, status=500)

    return JsonResponse({"status": "Success"}, status=200)


def generate_signature(payload: dict, secret_key: str) -> str:
    signed_payload = "".join([str(payload.get(k)) for k in payload])
    return hmac.new(
        secret_key.encode(), signed_payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()
