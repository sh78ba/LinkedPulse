# LinkedIn Profile API

A production-ready, reverse-engineered REST API built with FastAPI and Python 3.12+ that extracts and normalizes LinkedIn profile data via **direct HTTP requests only**.

> [!IMPORTANT]
> **Zero Browser Automation**: This implementation does not use browser automation (no Selenium, Playwright, Puppeteer, ChromeDriver, or Chromium). All LinkedIn communication is performed through direct HTTP requests using `httpx.AsyncClient`.

---

## Overview

The **LinkedIn Profile API** accepts a public LinkedIn profile URL (e.g., `https://www.linkedin.com/in/example/`) and returns comprehensive, structured profile data including basic demographics, work experience, education, skills, certifications, languages, and profile images.

---

## Assignment Requirements

- **Direct HTTP Only**: Purely reverse-engineered communication with LinkedIn HTTP endpoints without any headless browser overhead.
- **Authorized Session Integration**: Operates using standard LinkedIn session cookies (`li_at`, `JSESSIONID`) supplied via environment variables.
- **Security & Safety**: Full protection against Server-Side Request Forgery (SSRF), private IP access restrictions, and strict domain validation.
- **Robust Observability**: Structured JSON logging (`structlog`) with unique `request_id` correlation, latency metrics, and automatic redaction of sensitive credentials.
- **No Docker / No Test Overhead**: Lean codebase configured for immediate execution locally and on free PaaS platforms like Render.

---

## Features

- **Feature-Based Architecture**: Clear separation of concerns between core utilities, API routing, LinkedIn client protocols, and dedicated feature extractors.
- **Type-Safe Schemas**: Strictly typed Pydantic v2 data models for requests, internal representations, and API responses.
- **Defensive Extraction**: Robust parsing resilient against schema variations, missing optional fields, and multiple LinkedIn response payloads (Voyager Dash REST entities, ProfileView payloads, and embedded HTML metadata).
- **Resilient Networking**: Connection pooling, configurable timeouts, and controlled exponential backoff for transient network issues.
- **Interactive OpenAPI Specs**: Built-in Swagger UI (`/docs`) and ReDoc (`/redoc`).

---

## Architecture

The project follows a modular, feature-driven structure:

```text
linkedin-profile-api/
│
├── app/
│   ├── main.py                     # FastAPI application setup, middleware, and lifespan
│   │
│   ├── core/                       # Core system cross-cutting concerns
│   │   ├── config.py               # Pydantic Settings configuration
│   │   ├── logging.py              # Structured JSON logging & secret redaction
│   │   ├── exceptions.py           # Domain exception classes & error taxonomy
│   │   └── security.py             # SSRF prevention & LinkedIn URL validation
│   │
│   ├── api/                        # HTTP API Routing
│   │   ├── router.py               # Root and v1 router aggregator
│   │   └── health.py               # Lightweight /health check endpoint
│   │
│   ├── features/                   # Business domain features
│   │   └── profile/
│   │       ├── router.py           # POST /api/v1/profile endpoint definition
│   │       ├── service.py          # Profile retrieval orchestration workflow
│   │       ├── schemas.py          # Pydantic v2 schemas
│   │       ├── exceptions.py       # Profile domain exceptions
│   │       │
│   │       ├── linkedin/           # Reverse-engineered LinkedIn HTTP layer
│   │       │   ├── client.py       # Asynchronous HTTP client (httpx.AsyncClient)
│   │       │   ├── endpoints.py    # Isolated registry of LinkedIn endpoints
│   │       │   ├── models.py       # Raw payload container dataclasses
│   │       │   └── parser.py       # Master parser coordinating extractors
│   │       │
│   │       └── extractors/         # Single-responsibility data extractors
│   │           ├── basic.py        # Name, headline, location, about
│   │           ├── experience.py   # Work experience and positions
│   │           ├── education.py    # Degrees, schools, and activities
│   │           ├── skills.py       # Listed skills
│   │           ├── certifications.py # Licenses and certifications
│   │           ├── languages.py    # Spoken/written languages
│   │           └── images.py       # Profile avatar & banner image URLs
│   │
│   └── utils/                      # Reusable utilities
│       ├── url.py                  # Vanity ID extraction & URL normalization
│       └── retry.py                # Exponential backoff retry handler
│
├── .env.example                    # Sample environment configuration
├── .gitignore                      # Git ignore rules protecting credentials
├── requirements.txt                # Pinned production dependencies
├── pyproject.toml                  # Project metadata & Ruff linter configuration
└── README.md                       # Documentation
```

---

## Reverse Engineering Approach

The client communicates with LinkedIn using the reverse-engineered HTTP request flow observed during standard authorized sessions:

```text
Target Profile URL (https://www.linkedin.com/in/{vanity_id}/)
                        │
                        ▼
            URL Validation & SSRF Guard
                        │
                        ▼
            Extract Public Vanity ID
                        │
                        ▼
            LinkedInClient (httpx.AsyncClient)
            ├── 1. GET /voyager/api/identity/dash/profiles?q=memberIdentity...
            ├── 2. GET /voyager/api/identity/profiles/{id}/profileView
            └── 3. GET /in/{id}/ (HTML fallback for JSON-LD / code-blocks)
                        │
                        ▼
            Aggregated Raw Response Payload
                        │
                        ▼
            LinkedInParser
            ├── extract_basic_profile()
            ├── extract_experience()
            ├── extract_education()
            ├── extract_skills()
            ├── extract_certifications()
            ├── extract_languages()
            └── extract_images()
                        │
                        ▼
            Normalized ProfileResponse (Pydantic v2)
```

---

## LinkedIn HTTP Endpoint Discovery

All verified LinkedIn endpoints are isolated in `app/features/profile/linkedin/endpoints.py`:

| Endpoint | Method | Purpose | Required Auth / Headers |
|---|---|---|---|
| `/voyager/api/identity/dash/profiles` | `GET` | Primary Voyager Dash API retrieving structured entity graph | `li_at` cookie, `csrf-token`, `x-restli-protocol-version: 2.0.0` |
| `/voyager/api/identity/profiles/{public_id}/profileView` | `GET` | Detailed profile view containing positions, education, licenses | `li_at` cookie, `csrf-token` |
| `/in/{public_id}/` | `GET` | Profile webpage containing embedded JSON-LD and `<code>` store blobs | `li_at` cookie |

---

## Direct HTTP Request Strategy

1. **Session Reuse**: Requests utilize persistent connection pooling via `httpx.AsyncClient` with custom keep-alive settings.
2. **Standard Headers**: Emulates expected browser headers (`User-Agent`, `Accept: application/vnd.linkedin.normalized+json+2.0`, `x-restli-protocol-version: 2.0.0`).
3. **Multi-Source Resilience**: Attempts Voyager Dash API first, falls back to profile view endpoints and embedded HTML metadata when necessary.
4. **Transient Error Handling**: Automatically retries idempotent GET requests on transient `502`, `503`, `504` or timeout events with exponential backoff.

---

## Authentication / Session Configuration

Authentication uses credentials from your authorized LinkedIn browser session.

### Extracting Session Cookies from Browser:
1. Log into [LinkedIn](https://www.linkedin.com) in your web browser.
2. Open Developer Tools (`F12` or `Cmd+Option+I`) -> **Application** / **Storage** tab -> **Cookies** -> `https://www.linkedin.com`.
3. Locate and copy the value of the `li_at` cookie.
4. (Optional) Locate the `JSESSIONID` cookie value (e.g., `"ajax:1234567890123456789"`).
5. Set these in your `.env` file.

> [!CAUTION]
> Never commit `.env` or share your `li_at` session cookie.

---

## Data Extraction

Dedicated extractors under `app/features/profile/extractors/` parse normalized entities:

- **`basic.py`**: Extracts `name`, `headline`, `location`, `about`, and canonical `profile_url`.
- **`experience.py`**: Parses job title, company name, company URL, formatted date ranges (`MM/YYYY` or `Present`), and job descriptions.
- **`education.py`**: Extracts school name, degree title, field of study, and duration.
- **`skills.py`**: Extracts skill names deduplicated by name.
- **`certifications.py`**: Parses license names, issuing authorities, license numbers, verification URLs, issue and expiration dates.
- **`languages.py`**: Extracts language names and proficiency levels.
- **`images.py`**: Resolves avatar URLs and cover banners from LinkedIn vector image structures or OpenGraph tags.

---

## Data Normalization

All fields are normalized to standard Python primitive types or `None` / `[]` when absent:

```json
{
  "success": true,
  "profile": {
    "name": "Bill Gates",
    "headline": "Co-chair, Bill & Melinda Gates Foundation",
    "location": "Seattle, Washington, United States",
    "about": "Co-chair of the Bill & Melinda Gates Foundation...",
    "profile_url": "https://www.linkedin.com/in/williamhgates/",
    "images": [
      "https://media.licdn.com/dms/image/..."
    ]
  },
  "experience": [
    {
      "title": "Co-chair",
      "company": "Bill & Melinda Gates Foundation",
      "company_url": "https://www.linkedin.com/company/bill-&-melinda-gates-foundation/",
      "location": "Seattle, WA",
      "start_date": "2000",
      "end_date": "Present",
      "description": "Guided by the belief that every life has equal value..."
    }
  ],
  "education": [
    {
      "school": "Harvard University",
      "degree": null,
      "field_of_study": null,
      "start_date": "1973",
      "end_date": "1975",
      "description": null
    }
  ],
  "skills": [
    { "name": "Philanthropy" },
    { "name": "Software Development" }
  ],
  "certifications": [],
  "languages": []
}
```

---

## API Documentation

FastAPI provides automated interactive documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON Schema**: `http://localhost:8000/openapi.json`

---

## API Examples

### 1. Health Check
```bash
curl -s http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok"
}
```

### 2. Fetch Profile
```bash
curl -X POST http://localhost:8000/api/v1/profile \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.linkedin.com/in/williamhgates/"}'
```

---

## Error Handling

Standardized JSON error envelope across all error conditions:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_URL",
    "message": "Invalid LinkedIn profile URL provided."
  },
  "request_id": "a9f8b2c1d0e3"
}
```

### Common Error Codes:
- `INVALID_URL` (HTTP 400): Malformed URL or non-LinkedIn domain.
- `SSRF_VIOLATION` (HTTP 403): Target resolves to private IP, localhost, or link-local range.
- `AUTHENTICATION_FAILED` (HTTP 401): Session cookie expired or missing.
- `PROFILE_NOT_FOUND` (HTTP 404): Target profile does not exist or is inaccessible.
- `RATE_LIMIT_EXCEEDED` (HTTP 429): LinkedIn rate limit or security checkpoint triggered.
- `LINKEDIN_REQUEST_FAILED` (HTTP 502): LinkedIn gateway or connection error.

---

## Logging

Structured JSON logging configured via `structlog` with automated credential redaction:

```json
{
  "timestamp": "2026-08-28T14:32:18.591381Z",
  "level": "info",
  "logger": "app_main",
  "request_id": "3ab766b91226",
  "method": "POST",
  "path": "/api/v1/profile",
  "status_code": 400,
  "duration_ms": 1.43,
  "event": "request_completed"
}
```

Sensitive keys (`li_at`, `cookie`, `authorization`, `token`, `password`) are automatically replaced with `[REDACTED]`.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Environment mode (`development`, `production`) |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `HOST` | `0.0.0.0` | Bind host address |
| `PORT` | `8000` | Bind port (uses platform-assigned `$PORT` if set) |
| `LINKEDIN_SESSION_COOKIE` | `""` | Value of `li_at` cookie |
| `LINKEDIN_CSRF_TOKEN` | `""` | Value of `JSESSIONID` cookie (e.g. `ajax:...`) |
| `LINKEDIN_USER_AGENT` | `Mozilla/5.0...` | Custom User-Agent string |
| `LINKEDIN_TIMEOUT_SECONDS`| `15.0` | HTTP request timeout in seconds |
| `HTTP_MAX_RETRIES` | `2` | Max retries for transient HTTP errors |

---

## Local Setup

### 1. Clone & Prepare Environment
```bash
cd reverselinkedin
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Credentials
```bash
cp .env.example .env
# Edit .env and supply your LINKEDIN_SESSION_COOKIE
```

---

## Running the Application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Manual API Verification

### 1. Verify Health Endpoint
```bash
curl -i http://localhost:8000/health
```
*Expected*: HTTP 200 `{"status": "ok"}`

### 2. Verify SSRF Protection
```bash
curl -i -X POST http://localhost:8000/api/v1/profile \
  -H "Content-Type: application/json" \
  -d '{"url": "http://127.0.0.1:8080/evil"}'
```
*Expected*: HTTP 400 with code `INVALID_URL` or `SSRF_VIOLATION`.

### 3. Verify Path Validation
```bash
curl -i -X POST http://localhost:8000/api/v1/profile \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.linkedin.com/feed/"}'
```
*Expected*: HTTP 400 with `Invalid LinkedIn profile URL path`.

### 4. Verify Profile Fetching (with configured `.env`)
```bash
curl -i -X POST http://localhost:8000/api/v1/profile \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.linkedin.com/in/williamhgates/"}'
```
*Expected*: HTTP 200 with populated profile, experience, education, and skills.

---

## Deployment Notes

The application is cloud-ready for free hosting providers (e.g., Render, Railway, Fly.io):

1. **Build Command**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Start Command**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. Set environment variables (`LINKEDIN_SESSION_COOKIE`, `LINKEDIN_CSRF_TOKEN`, `LOG_LEVEL=INFO`) in your hosting dashboard.

---

## Security Considerations

- **No Credential Leakage**: Never logs raw session cookies, authorization headers, or auth tokens.
- **SSRF Hardening**: Resolves and validates DNS hostnames, blocking loops, private RFC 1918 subnets, and AWS/GCP metadata endpoints (`169.254.169.254`).
- **Input Sanitization**: Rejects non-profile paths and malformed strings before network requests are dispatched.

---

## Limitations

- **Session Expiration**: LinkedIn session cookies periodically expire and require updating in environment variables.
- **Rate Limits & Checkpoints**: Excessive querying from non-residential IP ranges may trigger LinkedIn anti-bot security challenges. The application surfaces these gracefully as `RATE_LIMIT_EXCEEDED` (HTTP 429) rather than attempting unauthorized evasion.
- **Private Profiles**: Profiles set to strict private visibility may return limited or empty data depending on the authorization level of the session user.

---

## Future Improvements

- Session pooling with rotation across multiple authorized tokens.
- Redis-backed response caching with configurable TTL to reduce redundant LinkedIn API calls.
- Webhook notification delivery for background batch profile enrichment.
