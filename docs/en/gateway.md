# Payment Gateway Sandbox API

A fake payment gateway for development and testing. Its flow and response format resemble the [IDPay](https://idpay.ir) payment service, so code written against this sandbox should be easy to adapt to a real gateway. It is **not affiliated with IDPay**, and **no real money is moved**.

- **Base path:** `/sandbox/gateway`
- **Format:** JSON requests and responses (except the fake payment page, which uses an HTML form)
- **Amounts:** in Rials
- **Note:** Error messages are returned in Persian.

## Flow

1. Your server calls **Create payment** and receives a transaction `id` and a payment `link`.
2. Redirect the customer to `link`. The fake payment page lets them confirm or cancel.
3. The customer is redirected back to your `callback` URL with the result in the query string.
4. Your server calls **Verify payment** to confirm the payment.

## Authentication

The API endpoints (`/payment` and `/payment/verify`) require your account's API key in the `X-API-Key` header.

```
X-API-Key: <your-api-key>
```

| Status | Meaning                                   |
|--------|-------------------------------------------|
| 401    | Header missing, or the API key is invalid |

## Transaction statuses

| Status | Meaning                        |
|--------|--------------------------------|
| `1`    | Created, waiting for payment   |
| `2`    | Payment canceled / failed      |
| `10`   | Paid, waiting for verification |
| `100`  | Paid and verified              |

## Create payment

`POST /sandbox/gateway/payment`

### Request body

| Field      | Type    | Required | Description                                                                                   |
|------------|---------|----------|-----------------------------------------------------------------------------------------------|
| `order_id` | string  | yes      | Your order identifier                                                                         |
| `amount`   | integer | yes      | Amount in Rials, from `1000` to `500000000`                                                   |
| `callback` | string  | yes      | Return URL, must start with `http://` or `https://`                                           |
| `name`     | string  | no       | Payer name                                                                                    |
| `phone`    | string  | no       | Payer mobile number (`09xxxxxxxxx`, `+989xxxxxxxxx` or `9xxxxxxxxx`; stored as `09xxxxxxxxx`) |
| `mail`     | string  | no       | Payer email address                                                                           |
| `desc`     | string  | no       | Description                                                                                   |

### Example

```bash
curl -X POST https://example.com/sandbox/gateway/payment \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "1001",
    "amount": 50000,
    "callback": "https://your-site.com/payment/callback",
    "name": "Ali",
    "phone": "09123456789",
    "mail": "ali@example.com",
    "desc": "Test order"
  }'
```

### Success response (201)

```json
{
  "id": "3f2b8c1e9a7d4e5f8b6a0c9d1e2f3a4b",
  "link": "https://example.com/sandbox/gateway/fake-pay/3f2b8c1e9a7d4e5f8b6a0c9d1e2f3a4b"
}
```

### Errors

| Status | Cause                                        |
|--------|----------------------------------------------|
| 400    | Body is not valid JSON or is empty           |
| 400    | A required field is missing or empty         |
| 400    | A field has the wrong type                   |
| 400    | `amount` is below 1,000 or above 500,000,000 |
| 400    | `callback` is not a valid HTTP/HTTPS URL     |
| 400    | `mail` is not a valid email address          |
| 401    | Missing or invalid API key                   |
| 411    | `phone` is not a valid phone number          |

## Fake payment page

`GET /sandbox/gateway/fake-pay/<id>`

Shows a page where the customer can confirm or cancel the payment. It is only available while the transaction status is `1`; otherwise it returns 404.

Submitting the page form (`POST`, field `action`) redirects the customer to your `callback`:

### Confirmed (`action=confirm`)

The transaction becomes status `10`, a random 5-digit `track_id` and a random fake card number are generated, and the customer is redirected to:

```
<callback>?status=10&track_id=12345&id=<id>&order_id=<order_id>&amount=<amount>&card_no=123456******7890
```

### Canceled (any other action)

The transaction becomes status `2`, and the customer is redirected to:

```
<callback>?status=2&id=<id>&order_id=<order_id>
```

> The parameters are appended with `?`, so use a `callback` URL without an existing query string.

## Verify payment

`POST /sandbox/gateway/payment/verify`

Call this from your server after the customer returns. Only transactions with status `10` can be verified, and each transaction can be verified once.

### Request body

| Field      | Type   | Required | Description                                        |
|------------|--------|----------|----------------------------------------------------|
| `id`       | string | yes      | Transaction `id` from *Create payment*             |
| `order_id` | string | yes      | The same `order_id` used when creating the payment |

### Example

```bash
curl -X POST https://example.com/sandbox/gateway/payment/verify \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"id": "3f2b8c1e9a7d4e5f8b6a0c9d1e2f3a4b", "order_id": "1001"}'
```

### Success response (200)

```json
{
  "status": "100",
  "track_id": "12345",
  "id": "3f2b8c1e9a7d4e5f8b6a0c9d1e2f3a4b",
  "order_id": "1001",
  "amount": "50000",
  "date": "1767225600",
  "payment": {
    "track_id": "12345",
    "amount": "50000",
    "card_no": "123456******7890",
    "hashed_card_no": "9F86D081884C7D659A2FEAA0C55AD015A3BF4F1B2B0B822CD15D6C15B0F00A08",
    "date": "1767225700"
  },
  "verify": {
    "date": "1767225800"
  }
}
```

All dates are Unix timestamps (seconds). `hashed_card_no` is the uppercase SHA-256 hash of the full (fake) card number.

### Errors

| HTTP | `error_code` | Cause                                                                        |
|------|--------------|------------------------------------------------------------------------------|
| 400  | –            | Body is not valid JSON or is empty                                           |
| 401  | –            | Missing or invalid API key                                                   |
| 406  | 31           | `id` or `order_id` is missing, empty or not a string                         |
| 400  | 52           | No transaction matches `id` and `order_id`                                   |
| 405  | 53           | Transaction cannot be verified (not paid yet, canceled, or already verified) |

Error body:

```json
{
  "error_code": 53,
  "error_message": "تایید پرداخت امکان پذیر نیست."
}
```

## Web panel

`GET /sandbox/gateway/panel` (login required)

Shows the logged-in user's transactions, newest first, 10 per page. Use `?page=N` to paginate.

Log in at `/sandbox/auth/login`. Accounts are created from the command line with `python register_user.py`.