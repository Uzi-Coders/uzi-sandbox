# SMS Sandbox API

A fake SMS service for development and testing. Its request/response format resembles the [Kavenegar](https://kavenegar.com) SMS API, so code written against this sandbox should be easy to adapt to a real provider. It is **not affiliated with Kavenegar**, and **no real SMS is ever sent**. Every valid request is stored as a log entry and reported as delivered.

- **Base path:** `/sandbox/sms`
- **Format:** JSON requests and responses
- **Note:** Error messages are returned in Persian.

## Authentication

Every API request must include your account's API key in the `X-API-Key` header.

```
X-API-Key: <your-api-key>
```

| Status | Meaning                                   |
|--------|-------------------------------------------|
| 401    | Header missing, or the API key is invalid |

## Send SMS

`POST /sandbox/sms/send`

### Request body

| Field      | Type   | Required | Description                          |
|------------|--------|----------|--------------------------------------|
| `receptor` | string | yes      | Recipient mobile number              |
| `message`  | string | yes      | Message text, at most 900 characters |

Accepted phone formats (all are normalized to `09xxxxxxxxx` when stored and returned):

| Input           | Stored as     |
|-----------------|---------------|
| `09123456789`   | `09123456789` |
| `+989123456789` | `09123456789` |
| `9123456789`    | `09123456789` |

### Example

```bash
curl -X POST https://example.com/sandbox/sms/send \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"receptor": "09123456789", "message": "Hello!"}'
```

### Success response (200)

```json
{
  "return": {
    "status": 200,
    "message": "تایید شد"
  },
  "entries": {
    "messageid": 1,
    "message": "Hello!",
    "status": 10,
    "statustext": "رسیده به گیرنده",
    "sender": 12345,
    "receptor": "09123456789",
    "date": 1767225600
  }
}
```

| Field        | Description                                                       |
|--------------|-------------------------------------------------------------------|
| `messageid`  | ID of the log entry                                               |
| `status`     | Always `10` (delivered) in the sandbox                            |
| `statustext` | Status description (`رسیده به گیرنده` = "delivered to recipient") |
| `sender`     | Sender number assigned to your account                            |
| `receptor`   | Normalized recipient number                                       |
| `date`       | Unix timestamp (seconds)                                          |

### Errors

| Status | Cause                                       |
|--------|---------------------------------------------|
| 400    | Body is not valid JSON or is empty          |
| 400    | `receptor` or `message` is missing or empty |
| 400    | `receptor` or `message` is not a string     |
| 401    | Missing or invalid API key                  |
| 411    | `receptor` is not a valid phone number      |
| 413    | `message` is longer than 900 characters     |

Error body:

```json
{
  "error": "فرمت شماره نامعتبر است."
}
```

## Web panel

`GET /sandbox/sms/panel` (login required)

Shows the SMS log of the logged-in user, newest first, 10 entries per page. Use the `?page=N` query parameter to paginate.

Log in at `/sandbox/auth/login`. Accounts are created from the command line with `python register_user.py`.