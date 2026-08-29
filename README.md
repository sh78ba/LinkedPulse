# LinkedIn Profile Reverse-Engineered API & Explorer

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?style=flat&logo=React&logoColor=black)](https://reactjs.org)
[![Vite](https://img.shields.io/badge/Vite-5+-646CFF.svg?style=flat&logo=Vite&logoColor=white)](https://vitejs.dev)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=Python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance, reverse-engineered LinkedIn Profile API and companion interactive web dashboard built with **FastAPI** and **React (Vite)**. It extracts structured profile data directly over **pure HTTP protocol** (`httpx.AsyncClient`) with **zero headless browser overhead** (no Selenium, Puppeteer, or Playwright).

---

## Table of Contents

- [Overview & Features](#overview--features)
- [Technical Approach & Reverse Engineering](#technical-approach--reverse-engineering)
- [Project Architecture](#project-architecture)
- [Getting Started & Local Setup](#getting-started--local-setup)
  - [Prerequisites](#prerequisites)
  - [1. Backend Setup](#1-backend-setup)
  - [2. Frontend Setup](#2-frontend-setup)
  - [3. How to Obtain LinkedIn Credentials](#3-how-to-obtain-linkedin-credentials)
- [API Reference & Response Schema](#api-reference--response-schema)
  - [Endpoint: POST /api/v1/profile](#endpoint-post-apiv1profile)
  - [Sample Response](#sample-response)
  - [Error Handling](#error-handling)
- [Deployment Guide (Public HTTPS)](#deployment-guide-public-https)
  - [Option A: Render / Railway / Fly.io](#option-a-render--railway--flyio)
  - [Option B: Docker Deployment](#option-b-docker-deployment)
- [Security & Anti-Abuse Protections](#security--anti-abuse-protections)
- [Known Limitations & Best Practices](#known-limitations--best-practices)

---

## Overview & Features

- **Pure HTTP Protocol**: Reverse-engineers LinkedIn internal Voyager Dash endpoints with sub-second response times (~300–800ms) and minimal memory footprint.
- **Comprehensive Profile Extraction**:
  - **Basic Info**: Full Name, Headline, Location (City, State, Country), Summary/About, Vanity URL.
  - **Images**: High-resolution CDN avatar URLs with multi-size artifact unwrapping (100px, 200px, 400px, 800px).
  - **Work Experience**: Positions, Job Titles, Company Names, Company LinkedIn URLs, Start/End Dates, Present Role flags, Descriptions.
  - **Education**: School/University Names, Degrees, Fields of Study, Start/End Years, Descriptions.
  - **Skills, Certifications & Languages**: Normalized skill arrays, issuing authorities, license credentials, and language proficiencies.
- **Clean Interactive Web UI**: Distraction-free dashboard with real-time profile lookup, preview cards, dynamic tabs, and 1-click JSON export.
- **Production-Ready**:
  - Structured JSON logging with `structlog` & correlation IDs (`X-Request-ID`).
  - SSRF protection against private IP ranges, AWS metadata, and malicious redirects.
  - In-memory sliding-window rate limiting.
  - Full OpenAPI 3.0 / Swagger documentation at `/docs`.

---

## Technical Approach & Reverse Engineering

### 1. The Voyager Dash API Layer
Modern LinkedIn uses an internal GraphQL/REST layer known as **Voyager Dash**. Rather than scraping rendered DOM nodes with browser automation, the backend queries the authoritative profile Dash endpoint:
```http
GET https://www.linkedin.com/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity={vanity_name}&decorationId=com.linkedin.voyager.dash.deco.identity.profile.FullProfileWithEntities-1
```

### 2. Authentication & Protocol Headers
To authenticate with Voyager Dash without triggering bot challenges:
- **`li_at`**: The session authentication cookie.
- **`JSESSIONID`**: Formatted as `"ajax:{csrf_token}"` in cookies.
- **`csrf-token`**: Sent in the request headers matching the `JSESSIONID` token.
- **`x-restli-protocol-version`**: `2.0.0`.
- **`x-requested-with`**: `XMLHttpRequest`.

### 3. Multi-Locale & Collection Resolution
LinkedIn returns profile strings as localized object maps (e.g., `multiLocaleHeadline: {"en_US": "..."}`, `multiLocaleSummary`, `multiLocaleTitle`). The extraction layer normalizes both plain strings and localized dictionaries. 

Additionally, positions (`profilePositionGroups`), educations (`profileEducations`), skills (`profileSkills`), and images (`displayImageReference.vectorImage.artifacts`) are unpacked recursively from the entity graph.

### 4. Fallback Architecture
If the Voyager Dash endpoint is rate-limited or restricted, the client seamlessly falls back to:
1. Unescaping embedded `<code>` data blocks containing Voyager store states in the HTML page.
2. Extracting Schema.org `Person` JSON-LD metadata (`worksFor`, `alumniOf`, `hasOccupation`, `address`).
3. Parsing OpenGraph meta tags (`og:title`, `og:description`, `og:image`).

---

## Project Architecture

```text
reverselinkedin/
├── backend/                        # FastAPI REST API
│   ├── app/
│   │   ├── main.py                 # Application factory & CORS configuration
│   │   ├── core/                   # Config, security, exceptions, structured logging
│   │   │   ├── config.py           # Pydantic BaseSettings (.env resolution)
│   │   │   ├── exceptions.py       # Domain exception hierarchy
│   │   │   ├── logging.py          # Structlog configuration
│   │   │   └── security.py         # SSRF validation & Rate limiter
│   │   ├── api/                    # API route definitions
│   │   │   ├── health.py           # Health probe (/health)
│   │   │   └── v1/
│   │   │       └── profile.py      # Profile extraction endpoint (/api/v1/profile)
│   │   ├── features/profile/       # Extraction engine
│   │   │   ├── linkedin/
│   │   │   │   ├── client.py       # Async HTTP client with connection pooling
│   │   │   │   ├── endpoints.py    # Voyager URL & header builders
│   │   │   │   └── parser.py       # Entity aggregator & collection unpacker
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
│   │       └── url_validator.py    # LinkedIn URL sanitization
│   ├── requirements.txt            # Pinned dependencies
│   ├── pyproject.toml              # Ruff linter & formatter configuration
│   └── .env.example                # Sample environment template
│
├── frontend/                       # React + Vite Interactive Dashboard
│   ├── src/
│   │   ├── components/             # Header, SearchBar, ProfileHero, Tabs, Views
│   │   ├── App.jsx                 # Application state container
│   │   ├── index.css               # Clean dark-mode design system
│   │   └── main.jsx                # React DOM entrypoint
│   ├── package.json                # Frontend dependencies
│   └── vite.config.js              # Vite server & API proxy
│
├── .gitignore                      # Strictly excludes .env and secrets
└── README.md                       # Complete documentation
```

---

## Getting Started & Local Setup

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & **npm**

---

### 1. Backend Setup

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate a Python virtual environment
python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
cp .env.example .env
```

Open `backend/.env` and add your LinkedIn session credentials (see [How to Obtain Credentials](#3-how-to-obtain-linkedin-credentials)):
```env
APP_ENV=development
PORT=8000
LINKEDIN_SESSION_COOKIE="your_li_at_cookie_here"
LINKEDIN_CSRF_TOKEN="ajax:your_jsessionid_here"
```

Start the FastAPI development server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend is now live at:
- **API Base**: `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/docs`
- **Health Probe**: `http://localhost:8000/health`

---

### 2. Frontend Setup

In a new terminal window:

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start the Vite development server
npm run dev
```

The frontend dashboard will be running at:
👉 **`http://localhost:5173`**

---

### 3. How to Obtain LinkedIn Credentials

1. Open [linkedin.com](https://www.linkedin.com) in your browser and ensure you are logged in.
2. Open Developer Tools (`F12` or `Cmd + Option + I`).
3. Go to the **Application** tab (Chrome/Edge) or **Storage** tab (Firefox).
4. Under **Cookies**, select `https://www.linkedin.com`.
5. Copy the following cookie values:
   - **`li_at`**: Paste into `LINKEDIN_SESSION_COOKIE`.
   - **`JSESSIONID`**: (e.g. `"ajax:1234567890123456789"`). Paste into `LINKEDIN_CSRF_TOKEN`.

---

## API Reference & Response Schema

### Endpoint: `POST /api/v1/profile`

Fetches and normalizes profile data from a LinkedIn profile URL.

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

#### Sample Response

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

The API uses standardized error payloads containing an error code, message, and unique `request_id`:

```json
{
  "detail": {
    "error_code": "INVALID_URL",
    "message": "Invalid LinkedIn URL: Must match linkedin.com/in/{vanity_name}",
    "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
  }
}
```

| HTTP Status | Error Code | Description |
|:---|:---|:---|
| `400 Bad Request` | `INVALID_URL` | Malformed or non-LinkedIn URL provided. |
| `400 Bad Request` | `SSRF_DETECTED` | Target resolves to internal IP or private subnet. |
| `401 Unauthorized` | `AUTHENTICATION_ERROR` | Session cookie (`li_at`) is expired or invalid. |
| `404 Not Found` | `PROFILE_NOT_FOUND` | Profile does not exist or has been deleted. |
| `429 Too Many Requests` | `RATE_LIMIT_EXCEEDED` | Request rate limit threshold reached. |
| `502 Bad Gateway` | `UPSTREAM_ERROR` | LinkedIn service error or network failure. |

---

## Deployment Guide (Public HTTPS)

### Option A: Render / Railway / Fly.io

1. **Deploy Backend**:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Root Directory: `backend`
   - Set Environment Variables:
     - `LINKEDIN_SESSION_COOKIE` = `your_li_at_cookie`
     - `LINKEDIN_CSRF_TOKEN` = `ajax:your_jsessionid`
     - `APP_ENV` = `production`

2. **Deploy Frontend**:
   - Build Command: `npm install && npm run build`
   - Publish Directory: `frontend/dist`
   - Root Directory: `frontend`
   - Set Environment Variable: `VITE_API_URL` = `https://your-backend-api.onrender.com`

---

### Option B: Docker Deployment

Create a `Dockerfile` in `backend/`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Run with Docker:
```bash
docker build -t linkedin-api ./backend
docker run -p 8000:8000 --env-file ./backend/.env linkedin-api
```

---

## Security & Anti-Abuse Protections

1. **SSRF Guard (`app/core/security.py`)**: Sanitizes and resolves all target hostnames before sending requests, dropping private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopbacks (`127.0.0.1`), and cloud metadata services (`169.254.169.254`).
2. **Correlation ID Tracking**: Automatically assigns or propagates an `X-Request-ID` header on every inbound and outbound request for full auditability.
3. **Secret Isolation**: Pydantic BaseSettings reads strictly from runtime environment variables or ignored `.env` files.

---

## Known Limitations & Best Practices

- **Session Expiration**: LinkedIn `li_at` session cookies typically remain valid for several months. If the cookie expires, update `LINKEDIN_SESSION_COOKIE` in your `.env` or deployment dashboard.
- **Throttling & Rate Limits**: To prevent LinkedIn from challenging your backend account, keep extraction traffic within reasonable limits (e.g. < 50–100 requests per hour per session).
- **Private Profiles**: Profiles set to strictly private or restricted visibility by the user may omit certain sections (such as email, full connections list, or hidden skills).
- **Post-Graduation Verification**: Education degree names and start/end dates are populated when declared on the member's public card.

---
