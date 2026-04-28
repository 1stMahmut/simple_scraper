# Twitter / X Profile Scraper

A full-stack automation tool that scrapes public Twitter/X profiles via API, stores structured data in Airtable, and displays a live records table through a deployed web interface.

**Live:**
- Frontend — deployed on [Vercel](https://vercel.com)
- Backend API — deployed on [Render](https://simple-scraper-6qtn.onrender.com/health)
- Data storage — [Airtable](https://airtable.com)

---

## What It Does

1. User enters a Twitter/X username in the web form
2. The Flask backend calls the [Twitter-API45](https://rapidapi.com/alexanderxbx/api/twitter-api45) via RapidAPI to fetch the public profile + recent tweets
3. Structured data is pushed to an Airtable base via the Airtable REST API
4. The live table on the frontend refreshes automatically to show all scraped profiles

---

## Architecture

```
[Vercel]                  [Render]                    [External APIs]
index.html  ──POST /scrape──▶  app.py (Flask)  ──▶  RapidAPI (Twitter-API45)
            ◀── profile JSON ──                 ──▶  Airtable REST API
            ──GET /records──▶                   ◀──  Airtable records
            ◀── records JSON──
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vanilla HTML / CSS / JS — static, no framework |
| Backend | Python 3 · Flask · Gunicorn |
| Scraping | RapidAPI — Twitter-API45 (REST, JSON) |
| Storage | Airtable REST API (`urllib` — zero extra dependencies) |
| Deployment | Render (backend) · Vercel (frontend) |
| Config | `python-dotenv` · environment variables |

---

## Features

- **Profile data** — display name, bio, location, website, join date, follower / following counts, tweet count
- **Recent tweets** — last 10 tweets with likes, retweets, and reply counts
- **Live table** — all scraped profiles displayed in the frontend, fetched directly from Airtable
- **Auto-refresh** — table updates after every scrape; manual Refresh button also available
- **No browser automation** — uses a direct REST API call instead of Playwright/Selenium for speed and reliability

---

## Project Structure

```
simple_scraper/
├── app.py               # Flask API — /scrape, /records, /health endpoints
├── twitter_scraper.py   # RapidAPI wrapper — fetches profile + timeline
├── airtable_sender.py   # Airtable REST client — creates records
├── index.html           # Frontend — scrape form + live records table
├── requirements.txt     # Python dependencies
├── render.yaml          # Render deployment config
├── vercel.json          # Vercel static site config
└── .env                 # Local secrets (not committed)
```

---

## API Endpoints

### `GET /health`
Returns server status.
```json
{ "status": "ok" }
```

### `POST /scrape`
Scrapes a Twitter/X profile and saves it to Airtable.

**Request:**
```json
{ "username": "elonmusk" }
```

**Response:**
```json
{
  "success": true,
  "record_id": "recXXXXXXXXXXXXXX",
  "profile": {
    "username": "elonmusk",
    "display_name": "Elon Musk",
    "followers": 239000000,
    "following": 1317,
    "bio": "..."
  }
}
```

### `GET /records`
Returns all scraped profiles from Airtable.
```json
[
  { "Name": "elonmusk", "Display Name": "Elon Musk", "Followers": 239000000, ... },
  ...
]
```

---

## Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/1stMahmut/simple_scraper.git
cd simple_scraper
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:
```env
RAPIDAPI_KEY=your_rapidapi_key
AIRTABLE_API_KEY=your_airtable_personal_access_token
AIRTABLE_BASE_ID=your_airtable_base_id
AIRTABLE_TABLE=Table 1
```

**Getting your keys:**
- **RapidAPI key** — sign up at [rapidapi.com](https://rapidapi.com), subscribe to [Twitter-API45](https://rapidapi.com/alexanderxbx/api/twitter-api45) (free tier: 500 req/month), copy your key from the dashboard
- **Airtable token** — go to [airtable.com/create/tokens](https://airtable.com/create/tokens), create a Personal Access Token with `data.records:read`, `data.records:write`, and `schema.bases:read` scopes, then add your base under "Access"
- **Airtable Base ID** — open your base in Airtable and copy the `appXXXXXXXXXXXXXX` segment from the URL

### 5. Run locally
```bash
python app.py
```

The server runs at `http://localhost:5000`. Open `index.html` in a browser and update `API_URL` in the script tag to `http://localhost:5000`.

---

## Airtable Schema

The following fields must exist in your Airtable table:

| Field | Type |
|---|---|
| Name | Single line text (primary field) |
| Display Name | Single line text |
| Bio | Long text |
| Location | Single line text |
| Website | Single line text |
| Joined | Single line text |
| Followers | Number |
| Following | Number |
| Tweets Count | Number |
| Recent Tweets | Long text |

---

## Deployment

### Backend — Render

1. Push repo to GitHub
2. Create a new **Web Service** on [render.com](https://render.com) and connect the repo
3. Set **Build Command:** `pip install -r requirements.txt`
4. Set **Start Command:** `gunicorn app:app --timeout 120`
5. Add environment variables under **Settings → Environment:**
   - `RAPIDAPI_KEY`
   - `AIRTABLE_API_KEY`
   - `AIRTABLE_BASE_ID`
   - `AIRTABLE_TABLE`

### Frontend — Vercel

1. Import the repo on [vercel.com](https://vercel.com)
2. Leave **Root Directory** as `./` — Vercel auto-detects `index.html`
3. Deploy — no build step needed

---

## Dependencies

```
flask
flask-cors
gunicorn
python-dotenv
```

No browser automation libraries required. All HTTP communication uses Python's built-in `urllib`.
