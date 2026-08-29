# LinkedPulse — LinkedIn Profile Intelligence API & Explorer

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?style=flat&logo=React&logoColor=black)](https://reactjs.org)
[![Vite](https://img.shields.io/badge/Vite-5+-646CFF.svg?style=flat&logo=Vite&logoColor=white)](https://vitejs.dev)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=Python&logoColor=white)](https://www.python.org)


A high-performance, reverse-engineered REST API and companion web dashboard built with **FastAPI** and **React (Vite)**. It extracts structured LinkedIn profile data over **pure HTTP protocol** (`httpx.AsyncClient`) with **zero headless browser overhead**.

---

## Table of Contents

- [Overview & Features](#overview--features)
- [Reverse-Engineering Technical Approach](#reverse-engineering-technical-approach)
- [LinkedIn HTTP Endpoint Discovery](#linkedin-http-endpoint-discovery)
- [Project Architecture](#project-architecture)
- [Data Extraction & Normalization](#data-extraction--normalization)
- [Quickstart & Local Setup](#quickstart--local-setup)
  - [1. Backend Setup](#1-backend-setup)
  - [2. Frontend Setup](#2-frontend-setup)
  - [3. Extracting Session Credentials](#3-extracting-session-credentials)
- [API Reference & Documentation](#api-reference--documentation)
  - [Endpoints Overview](#endpoints-overview)
  - [POST /api/v1/profile](#post-apiv1profile)
  - [Sample JSON Output](#sample-json-output)
  - [Error Handling](#error-handling)
- [Observability & Structured Logging](#observability--structured-logging)
- [Security & Anti-Abuse Protections](#security--anti-abuse-protections)
- [Production Deployment Guide](#production-deployment-guide)
  - [Deploying Backend (Render / Railway)](#deploying-backend-render--railway)
  - [Deploying Frontend (Vercel / Netlify)](#deploying-frontend-vercel--netlify)
  - [Docker Containerization](#docker-containerization)
- [Known Limitations & Best Practices](#known-limitations--best-practices)
- [Future Improvements](#future-improvements)

---

## Overview & Features

- **⚡ Direct HTTP Engine**: Communicates directly with LinkedIn's internal GraphQL/REST endpoints using `httpx.AsyncClient` with connection pooling, retries, and explicit timeouts.
- **🚀 Zero Browser Automation**: No heavy headless browser memory overhead (uses ~30MB RAM compared to ~500MB+ for Chromium/Playwright).
- **📋 Full Profile Extraction**:
  - **Basic Demographics**: Full Name, Headline, Formatted Location (City, State, Country), Summary/About, Canonical Vanity URL.
  - **Profile Images**: High-resolution CDN avatar URLs with multi-size artifact unwrapping (100px, 200px, 400px, 800px).
  - **Work Experience**: Position Titles, Company Names, Company LinkedIn URLs, Start/End Dates (`MM/YYYY` or `Present`), Descriptions.
  - **Education**: School/University Names, Degree Titles, Fields of Study, Start/End Years, Descriptions.
  - **Skills, Certifications & Languages**: Normalized skill arrays, issuing authorities, verification links, and language proficiencies.
- **💻 LinkedPulse Web Dashboard**: Clean, human-designed React + Vite UI with instant profile lookup, preview cards, dynamic data tabs, and 1-click JSON export.
- **🛡️ Enterprise Security**:
  - SSRF protection against private IP ranges, loopbacks, and AWS/GCP metadata endpoints (`169.254.169.254`).
  - Strict input sanitization rejecting non-profile URLs before network dispatch.
- **📊 Robust Observability**: Structured JSON logging (`structlog`) with correlation IDs (`X-Request-ID`), duration tracking, and automatic credential redaction.

---

## Reverse-Engineering Technical Approach

Modern LinkedIn does not render raw HTML pages on every navigation; instead, its web client communicates with an internal API layer known as **Voyager Dash** (built on Rest.li).

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

### 1. The Voyager Dash Protocol Layer
The backend queries the primary profile decoration endpoint:
```http
GET https://www.linkedin.com/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity={vanity_id}&decorationId=com.linkedin.voyager.dash.deco.identity.profile.FullProfileWithEntities-1
```

### 2. Authentication & Protocol Headers
To authenticate with Voyager Dash without triggering anti-bot challenges:
- **`li_at`**: The session authentication cookie.
- **`JSESSIONID`**: Formatted as `"ajax:{csrf_token}"` in cookies.
- **`csrf-token`**: Sent in the request headers matching the `JSESSIONID` token.
- **`x-restli-protocol-version`**: `2.0.0`.
- **`x-requested-with`**: `XMLHttpRequest`.

### 3. Multi-Locale & Collection Resolution
LinkedIn returns profile strings as localized object maps (e.g., `multiLocaleHeadline: {"en_US": "..."}`, `multiLocaleSummary`, `multiLocaleTitle`). The extraction layer normalizes both plain strings and localized dictionaries.

Positions (`profilePositionGroups`), educations (`profileEducations`), skills (`profileSkills`), and vector images (`displayImageReference.vectorImage.artifacts`) are unpacked recursively from the entity graph.

### 4. Fallback Architecture
If the Voyager Dash endpoint is rate-limited or restricted, the client seamlessly falls back to:
1. Unescaping embedded `<code>` data blocks containing Voyager store states in the HTML page.
2. Extracting Schema.org `Person` JSON-LD metadata (`worksFor`, `alumniOf`, `hasOccupation`, `address`).
3. Parsing OpenGraph meta tags (`og:title`, `og:description`, `og:image`).

---

## LinkedIn HTTP Endpoint Discovery

All verified LinkedIn endpoints are isolated in `backend/app/features/profile/linkedin/endpoints.py`:

| Endpoint | Method | Purpose | Required Auth / Headers |
|---|---|---|---|
| `/voyager/api/identity/dash/profiles` | `GET` | Primary Voyager Dash API retrieving structured entity graph | `li_at` cookie, `csrf-token`, `x-restli-protocol-version: 2.0.0` |
| `/voyager/api/identity/profiles/{id}/profileView` | `GET` | Detailed profile view containing positions, education, licenses | `li_at` cookie, `csrf-token` |
| `/in/{id}/` | `GET` | Profile webpage containing embedded JSON-LD and `<code>` store blobs | `li_at` cookie |

---

## Project Architecture

```text
reverselinkedin/
├── backend/                        # FastAPI REST API
│   ├── app/
│   │   ├── main.py                 # Application factory, CORS, and lifespan
│   │   ├── core/                   # Cross-cutting concerns
│   │   │   ├── config.py           # Pydantic BaseSettings (.env resolution)
│   │   │   ├── exceptions.py       # Domain exception hierarchy
│   │   │   ├── logging.py          # Structured JSON logging & secret redaction
│   │   │   └── security.py         # SSRF validation & Rate limiter
│   │   ├── api/                    # HTTP API Routing
│   │   │   ├── router.py           # Root and v1 router aggregator
│   │   │   ├── health.py           # Root (/) & health (/health) endpoints
│   │   │   └── v1/
│   │   │       └── profile.py      # Profile extraction endpoint (/api/v1/profile)
│   │   ├── features/profile/       # Extraction engine
│   │   │   ├── linkedin/
│   │   │   │   ├── client.py       # Async HTTP client with connection pooling
│   │   │   │   ├── endpoints.py    # Isolated registry of LinkedIn endpoints
│   │   │   │   ├── models.py       # Raw payload container dataclasses
│   │   │   │   └── parser.py       # Master parser coordinating extractors
│   │   │   ├── extractors/         # Defensive feature extractors
│   │   │   │   ├── basic.py        # Name, headline, location, about
│   │   │   │   ├── experience.py   # Work experience timeline
│   │   │   │   ├── education.py    # Degrees & schools
│   │   │   │   ├── skills.py       # Skill tags
│   │   │   │   ├── certifications.py # Licenses & certs
│   │   │   │   ├── languages.py    # Spoken/written languages
│   │   │   │   └── images.py       # High-res CDN vector images
│   │   │   ├── schemas.py          # Pydantic output schemas
│   │   │   └── service.py          # Profile orchestration service
│   │   └── utils/
│   │       ├── url.py              # Vanity ID extraction & URL normalization
│   │       └── retry.py            # Exponential backoff retry handler
│   ├── requirements.txt            # Pinned dependencies
│   ├── pyproject.toml              # Ruff linter & formatter configuration
│   └── .env.example                # Sample environment template
│
├── frontend/                       # React + Vite Interactive Dashboard
│   ├── src/
│   │   ├── components/             # Header, SearchBar, ProfileHero, Tabs, Views
│   │   ├── config.js               # Centralized API Base URL configuration
│   │   ├── App.jsx                 # Application state container
│   │   ├── index.css               # Clean dark-mode design system
│   │   └── main.jsx                # React DOM entrypoint
│   ├── package.json                # Frontend dependencies
│   └── vite.config.js              # Vite server & API proxy
│
├── .gitignore                      # Strictly excludes secret .env files
├── .env.example                    # Root environment template
└── README.md                       # Comprehensive documentation
```

---

## Data Extraction & Normalization

Dedicated extractors under `backend/app/features/profile/extractors/` parse normalized entities:

- **`basic.py`**: Extracts `name`, `headline`, `location`, `about`, and canonical `profile_url`.
- **`experience.py`**: Parses job title, company name, company URL, formatted date ranges (`MM/YYYY` or `Present`), and job descriptions.
- **`education.py`**: Extracts school name, degree title, field of study, and duration.
- **`skills.py`**: Extracts skill names deduplicated by name.
- **`certifications.py`**: Parses license names, issuing authorities, license numbers, verification URLs, issue and expiration dates.
- **`languages.py`**: Extracts language names and proficiency levels.
- **`images.py`**: Resolves avatar URLs and cover banners from LinkedIn vector image structures or OpenGraph tags.

---

## Quickstart & Local Setup

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & **npm**

---

### 1. Backend Setup

```bash
cd backend

# Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
```

Open `backend/.env` and add your session cookies:
```env
APP_ENV=development
PORT=8000
LINKEDIN_SESSION_COOKIE="your_li_at_cookie_value_here"
LINKEDIN_CSRF_TOKEN="ajax:your_jsessionid_here"
```

Start the backend server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend URLs:
- **API Base**: `http://localhost:8000`
- **Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

---

### 2. Frontend Setup

In a new terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Open your browser at 👉 **`http://localhost:5173`**

---

### 3. Extracting Session Credentials

1. Log into [LinkedIn](https://www.linkedin.com) in your web browser.
2. Open Developer Tools (`F12` or `Cmd + Option + I`).
3. Go to the **Application** / **Storage** tab -> **Cookies** -> `https://www.linkedin.com`.
4. Copy the following cookie values:
   - **`li_at`**: Paste into `LINKEDIN_SESSION_COOKIE`.
   - **`JSESSIONID`**: (e.g. `"ajax:1234567890123456789"`). Paste into `LINKEDIN_CSRF_TOKEN`.

---

## API Reference & Documentation

### Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Root API metadata & documentation navigation links |
| `GET` | `/health` | Lightweight service health probe |
| `GET` | `/docs` | Interactive OpenAPI Swagger UI |
| `GET` | `/redoc` | Interactive ReDoc documentation |
| `POST` | `/api/v1/profile` | Extract structured profile details from a LinkedIn URL |

---

### `POST /api/v1/profile`

#### Request Headers
```http
Content-Type: application/json
```

#### Request Body
```json
{
  "url": "https://www.linkedin.com/in/sundarpichai/"
}
```

#### Sample JSON Output

```json
{
  "success": true,
  "profile": {
    "name": "Sundar Pichai",
    "headline": "CEO at Google",
    "location": "Mountain View, California, United States",
    "about": "CEO of Google and Alphabet. Focused on organizing the world's information and making it universally accessible and useful, building great products, and developing advanced technologies, including AI, to help people everywhere.",
    "profile_url": "https://www.linkedin.com/in/sundarpichai/",
    "images": [
      "https://media.licdn.com/dms/image/v2/D5603AQHC8_1s7IHNHg/profile-displayphoto-scale_400_400/B56Z36YnjDIkAg-/0/1778022254687?e=1789603200&v=beta&t=3wDEFw5o8sWnrrbbl5AvjbHgXLuUWOR3czCBZcdFzgk",
      "https://media.licdn.com/dms/image/v2/D5603AQHC8_1s7IHNHg/profile-displayphoto-crop_800_800/B56Z36YnjDIkAI-/0/1778022254573?e=1789603200&v=beta&t=swDXoNQIbp109_hm89VpNJ9PxaZuj94np_mZqBxH278"
    ]
  },
  "experience": [
    {
      "title": "CEO",
      "company": "Google",
      "company_url": "https://www.linkedin.com/company/1441/",
      "location": null,
      "start_date": "2015",
      "end_date": "Present",
      "description": null
    },
    {
      "title": "Product Management + Leadership",
      "company": "Google",
      "company_url": "https://www.linkedin.com/company/1441/",
      "location": null,
      "start_date": "04/2004",
      "end_date": "2015",
      "description": null
    }
  ],
  "education": [
    {
      "school": "The Wharton School",
      "degree": "MBA",
      "field_of_study": null,
      "start_date": null,
      "end_date": null,
      "description": null
    },
    {
      "school": "Stanford University",
      "degree": "MS",
      "field_of_study": "Materials Science and Engineering",
      "start_date": null,
      "end_date": null,
      "description": null
    },
    {
      "school": "Indian Institute of Technology, Kharagpur",
      "degree": "B. Tech",
      "field_of_study": null,
      "start_date": null,
      "end_date": null,
      "description": null
    }
  ],
  "skills": [],
  "certifications": [],
  "languages": []
}
```

---

### Error Handling

All error responses use a standardized JSON error envelope:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_URL",
    "message": "Invalid LinkedIn profile URL path. Expected format: https://www.linkedin.com/in/<profile-id>/"
  },
  "request_id": "3ab766b91226"
}
```

| HTTP Status | Error Code | Description |
|---|---|---|
| `400 Bad Request` | `INVALID_URL` | Malformed URL, missing vanity path, or non-LinkedIn domain. |
| `400 Bad Request` | `SSRF_DETECTED` | Target resolves to loopback, private RFC 1918 range, or metadata IP. |
| `401 Unauthorized` | `AUTHENTICATION_ERROR` | Session cookie (`li_at`) expired or missing. |
| `404 Not Found` | `PROFILE_NOT_FOUND` | Profile does not exist or has been removed. |
| `429 Too Many Requests` | `RATE_LIMIT_EXCEEDED` | Request rate limit threshold triggered. |
| `502 Bad Gateway` | `UPSTREAM_ERROR` | LinkedIn service failure or network error. |

---

## Observability & Structured Logging

Structured JSON logging is powered by `structlog` with automated credential redaction and latency tracking:

```json
{
  "timestamp": "2026-08-28T14:32:18.591381Z",
  "level": "info",
  "logger": "app_main",
  "request_id": "3ab766b91226",
  "method": "POST",
  "path": "/api/v1/profile",
  "status_code": 200,
  "duration_ms": 482.15,
  "event": "request_completed"
}
```

Sensitive keys (`li_at`, `cookie`, `authorization`, `token`, `password`) are automatically redacted with `[REDACTED]`.

---

## Security & Anti-Abuse Protections

1. **SSRF Guard (`backend/app/core/security.py`)**: Sanitizes and resolves all target hostnames before sending requests, dropping private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopbacks (`127.0.0.1`), and cloud metadata services (`169.254.169.254`).
2. **Correlation ID Tracking**: Automatically assigns or propagates an `X-Request-ID` header on every inbound and outbound request.
3. **Secret Isolation**: Pydantic BaseSettings reads strictly from runtime environment variables or ignored `.env` files.

---

## Production Deployment Guide

### Deploying Backend (Render / Railway)

1. **Create Web Service**:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
2. **Environment Variables**:
   - `APP_ENV`: `production`
   - `LINKEDIN_SESSION_COOKIE`: `your_li_at_cookie_value`
   - `LINKEDIN_CSRF_TOKEN`: `ajax:your_jsessionid_value`
   - `CORS_ORIGINS`: `["https://your-frontend.vercel.app"]`

---

### Deploying Frontend (Vercel / Netlify)

1. **Import Repository**:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
2. **Environment Variable**:
   - `VITE_API_URL`: `https://your-backend-service.onrender.com`

---

### Docker Containerization

To run the backend with Docker:

```bash
# Build image
docker build -t linkedpulse-api ./backend

# Run container with environment variables
docker run -p 8000:8000 --env-file ./backend/.env linkedpulse-api
```

---

## Known Limitations & Best Practices

- **Session Expiration**: LinkedIn `li_at` cookies periodically expire and require updating in environment variables.
- **Throttling & Rate Limits**: To keep your session safe, maintain extraction volume within reasonable limits (< 50–100 requests/hour per session).
- **Private Profiles**: Profiles set to strictly private visibility by the member may omit certain sections depending on session authorization.

---

## Future Improvements

- Multi-session token pooling and automatic cookie rotation.
- Redis-backed response caching with configurable TTL to minimize upstream calls.
- Webhook delivery for asynchronous batch profile enrichment.

---

## License

MIT License © 2026. Built for reverse-engineering research and API integration.
