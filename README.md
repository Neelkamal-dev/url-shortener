# ✂️ Snip — URL Shortener

A production-ready URL shortener built with **Python + Flask + PostgreSQL**, deployable to Render for free.

## Features
- Shorten any URL to a 6-character code
- Optional custom short codes (e.g. `/my-link`)
- Click tracking per URL
- Delete links
- REST API
- PostgreSQL database (production-grade)

---

## Project Structure

```
url_shortener/
├── app.py           # Flask app & routes
├── database.py      # PostgreSQL connection + schema
├── url_service.py   # Business logic
├── render.yaml      # One-click Render deployment config
├── requirements.txt
└── templates/
    ├── index.html
    └── 404.html
```

---

## Local Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your local PostgreSQL URL
set DATABASE_URL=postgresql://user:password@localhost:5432/snip   # Windows
export DATABASE_URL=postgresql://user:password@localhost:5432/snip # Mac/Linux

# 4. Run
python app.py
```

---

## Deploy to Render (Free)

1. Push this folder to a GitHub repo
2. Go to render.com → New → Blueprint
3. Connect your GitHub repo
4. Render auto-reads `render.yaml` and creates:
   - Web service (your app)
   - Free PostgreSQL database
5. After deploy, set `BASE_URL` env var to your Render URL
   e.g. `https://snip-url-shortener.onrender.com`

---

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/shorten` | Shorten a URL |
| GET | `/api/urls` | List all links |
| GET | `/api/stats/<code>` | Get click stats |
| DELETE | `/api/urls/<code>` | Delete a link |
| GET | `/<code>` | Redirect to original URL |

### Example

```bash
curl -X POST https://your-app.onrender.com/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com", "custom_code": "gh"}'
```
