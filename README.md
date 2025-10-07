# Palmer - All Hackathons in the Palm of Your Hand

> **The problem?** Hackathons are scattered across dozens of platforms.

> **The solution?** Palmer scrapes, aggregates, and serves every hackathon in existence through one API.

---
## The Vision

```bash
GET /api/hackathons?location=nearby&status=upcoming
```

With a nice frontend to showcase the api, making it easy for users to discover hackathons.

---

##  Why This Matters

### For Students & Hackers
- **Save time** - Find opportunities quickly
- **Make informed decisions** - Compare prizes, locations, and themes easily

### For Organizers
- **Increased visibility** - Your hackathon reaches more potential participants

---

## What Makes Palmer Different

### 1. **Comprehensive Coverage**
We scrape from everywhere:
- Devpost (largest platform)
- MLH (official collegiate)
- Hackathon.com
- University sites
- Corporate sites
- *...and growing*

### 2. **Smart Data**
Not just basic info - we extract:
- Precise dates & deadlines
- Full prize breakdowns
- Eligibility requirements (age, location, student status)
- Judges & judging criteria
- Sponsors
- Tags & themes
- Detailed descriptions

### 3. **Built for Scale**
- **Auto-updating** - Celery workers refresh data every 6 hours
- **Fast queries** - PostgreSQL with smart indexing
- **Reliable** - Retry logic, fallbacks, and error handling
- **Respectful** - Rate limiting and robots.txt compliance

---

## Use Cases

### Main Hackathon Discovery Platform
Palmer is the backend for a hackathon finder with filtering, maps, and recommendations.

### Discord/Slack Bots
Notify communities about relevant upcoming hackathons.

### University Portals
Integrate hackathon listings directly into student dashboards.

### Analytics Dashboards
Track trends in hackathon themes, prizes, and locations.

### Personal Assistants
"Hey Siri, what hackathons are near me this month?"

---

## Tech Stack

**Backend:**
- **Scrapy** - Industrial-strength web scraping
- **Playwright** - JavaScript-heavy site handling
- **FastAPI** - Lightning-fast API framework
- **PostgreSQL** - Robust data storage
- **Celery** - Scheduled background jobs

**API Architecture:**
```
Devpost/MLH/etc. → Scrapers → PostgreSQL → FastAPI → Endpoint
                      ↓
                   Celery (every 6h)
```

---

## The Market

- **3,000+** hackathons happen annually worldwide
- **200,000+** student hackers actively participate
- **$50M+** in prizes awarded each year
- **Growing 20%+** year-over-year

**But discovery is still broken.** Palmer fixes that.
---

## The Opportunity

### Short-term
- Launch free public API
- Build a nice frontend to showcase the api

---
