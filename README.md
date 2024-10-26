# Django Webhook Integration

This project is a Django application that implements a webhook endpoint to receive notifications from YaYa Wallet.
The application verifies the integrity of the incoming requests by checking the HMAC signature and ensures the request's
timestamp is within an acceptable tolerance window.

1. **Environment**:  assumes you are using Python 3.10 
2. **Dependencies**: All necessary packages are listed in the `requirements.txt` file.
3. **Database**: The application is set up to use PostgreSQL as the database. Ensure that your PostgreSQL server is running and accessible.

## Problem Solving Approach

To implement the webhook functionality, I used the divide-and-conquer approach to break down the problem into manageable components:

1. Webhook Endpoint Creation:
   - Implemented a Django view that listens for incoming POST requests at a specific endpoint.
   - Parsed the incoming JSON payload to extract necessary fields, including the signature and timestamp.

2. Signature Verification:
   - Extracted the `YAYA-SIGNATURE` from the request headers.
   - Constructed the `signed_payload` by concatenating values from the payload to create a string representation.
   - Generated an expected HMAC signature using the provided secret key and the signed payload.
   - Compared the received signature with the expected signature using `hmac.compare_digest()` for secure comparison.

3. Timestamp Validation:
   - Retrieved the `timestamp` from the payload and calculated the time difference between the current time and the received timestamp.
   - Ensured the timestamp is within a 5-minute tolerance using a configurable setting.
  
4. Data Storage:
   - Stored the payload in a PostgreSQL database for further processing or auditing.

5. Testing:
   - Wrote unit tests to verify the functionality of the webhook endpoint, ensuring that valid signatures are accepted and invalid ones are rejected.
   - Used Django's testing framework to simulate incoming requests and validate the expected outcomes.

Run Migrations:
   Ensure your database is set up and run the following command to apply migrations:

   python manage.py migrate

Run the Development Server
    python manage.py runserver

Run Tests: Execute the tests to validate the functionality:
    python manage.py test

