# Uzi Sandbox

A small Flask app that provides fake **payment gateway** and **SMS** APIs for development and testing.

- The **payment gateway** resembles the [IDPay](https://idpay.ir) service.
- The **SMS service** resembles the [Kavenegar](https://kavenegar.com) API.

This project is not affiliated with IDPay or Kavenegar. No real payments are made and no real SMS messages are sent.

## Features

- Payment gateway: create a transaction, pay (or cancel) on a fake payment page, get redirected to your callback, then verify the payment.
- SMS: send messages through a JSON API; every message is stored and reported as delivered.
- Per-user API keys (`X-API-Key` header).
- Web panels with login to browse your transactions and SMS logs.
- Persian error messages, with documentation in English and Persian.

## Documentation

| Topic           | English                                  | فارسی                                    |
|-----------------|------------------------------------------|------------------------------------------|
| Payment gateway | [docs/en/gateway.md](docs/en/gateway.md) | [docs/fa/gateway.md](docs/fa/gateway.md) |
| SMS             | [docs/en/sms.md](docs/en/sms.md)         | [docs/fa/sms.md](docs/fa/sms.md)         |

## Project structure

```
.
├── app.py               # Flask app, config, login manager
├── blueprints/          # auth, sms and gateway routes
├── database/            # SQLAlchemy instance and models
├── utils/               # decorators, forms, helpers, validators
├── templates/           # HTML templates
├── static/              # CSS and images
├── docs/                # API docs (en, fa)
├── tests/               # test suite
├── register_user.py     # CLI script to create users
├── requirements.txt
└── Dockerfile
```

## Getting started

### Requirements

- Python 3.10 or newer (Flask 3.1 requires it)

### Install

```bash
python -m venv .venv
source .venv/bin/activate      # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configure

The app needs a `SECRET_KEY` and refuses to start without it. Create a `.env` file in the project root:

```
SECRET_KEY=replace-with-a-long-random-value
```

You can generate a value with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

The SQLite database is created automatically at `database/db.sqlite3` on first start.

### Create a user

```bash
python register_user.py
```

The script asks for a username and a password. Each user gets their own API key.

### Run

For development:

```bash
flask --app app run --debug
```

For production, use gunicorn:

```bash
gunicorn app:app
```

The app is served under the `/sandbox` prefix, for example `http://127.0.0.1:5000/sandbox/`.

## Endpoints

| Endpoint                          | Method    | Auth    | Description       |
|-----------------------------------|-----------|---------|-------------------|
| `/sandbox/`                       | GET       | login   | Home page         |
| `/sandbox/auth/login`             | GET, POST | –       | Login page        |
| `/sandbox/auth/logout`            | POST      | login   | Log out           |
| `/sandbox/sms/send`               | POST      | API key | Send an SMS       |
| `/sandbox/sms/panel`              | GET       | login   | SMS log           |
| `/sandbox/gateway/payment`        | POST      | API key | Create a payment  |
| `/sandbox/gateway/fake-pay/<id>`  | GET, POST | –       | Fake payment page |
| `/sandbox/gateway/payment/verify` | POST      | API key | Verify a payment  |
| `/sandbox/gateway/panel`          | GET       | login   | Transaction list  |

API requests authenticate with the `X-API-Key` header. See the docs above for request and response details.

### Quick example

```bash
# Send an SMS
curl -X POST http://127.0.0.1:5000/sandbox/sms/send \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"receptor": "09123456789", "message": "Hello!"}'

# Create a payment
curl -X POST http://127.0.0.1:5000/sandbox/gateway/payment \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"order_id": "1001", "amount": 50000, "callback": "https://your-site.com/callback"}'
```

## Tests

The tests live in `tests/`. If you use pytest, install it first (it is not listed in `requirements.txt`):

```bash
pip install pytest
pytest
```

## Docker

A `Dockerfile` is included for building a container image:

```bash
docker build -t sandbox .
```

Remember to provide `SECRET_KEY` to the container as an environment variable.

## Notes

- This is a testing tool. Don't expose it publicly with real user data or use it as a real payment or SMS provider.
- Amounts are in Rials.