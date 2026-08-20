# 🎓 ScholarSeek

**[Live Demo](https://scholarship-finder-silk.vercel.app/)** · **[GitHub Repo](https://github.com/Manvi1670/Scholarship_finder)**

A full-stack scholarship discovery platform that scrapes real scholarships from multiple sources and ranks them individually for each student — instead of showing every user the same undifferentiated list, like most existing scholarship aggregators do.

Every scholarship is scored against a student's actual profile (course, CPI, region) across relevance, deadline urgency, and award amount, with the reasoning behind each match surfaced directly in the UI.

## ✨ Features

- 🔐 **Authentication** — JWT-based registration and login
- 🎯 **Personalized Matching Engine** — scholarships are scored per student on course/field relevance, region, CPI eligibility, deadline urgency, and award amount, then ranked best-match-first with visible tags explaining *why* each one matched
- 🎛️ **Dynamic Filtering** — by category (Monetary, Tuition Waiver, Mixed, Other), deadline range (Week/Month/Six Months/Always Open), free-text search, and eligibility keyword search
- 📄 **Detailed Scholarship Pages** — eligibility criteria, award amount, contact info, and a direct apply link
- 👤 **Profile Management** — students set their course, CPI, and region, which directly drives the matching engine
- 🤖 **Fully Automated Data Pipeline** — a scheduled GitHub Actions workflow re-scrapes both data sources and refreshes the database twice a week with zero manual steps

## 🌐 Data Sources

Scraped from two independent sources, deduplicated against each other, and normalized into a single schema:

- **[Buddy4Study](https://www.buddy4study.com)** — India's largest scholarship aggregator (JS-rendered listings via Selenium, detail pages via static requests)
- **[National Scholarship Portal (NSP)](https://scholarships.gov.in)** — India's official government portal, with eligibility criteria extracted from linked PDF guideline documents

## 🖥️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React (Vite), React Router — deployed on Vercel |
| **Backend** | Node.js, Express, JWT auth (`bcrypt`, `jsonwebtoken`) |
| **Database** | MongoDB Atlas |
| **Scraping** | Python — `requests`, `BeautifulSoup`, `Selenium`, `pdfplumber` |
| **Automation** | GitHub Actions (scheduled scraper pipeline) |

## 🏗️ Architecture

```
Python scrapers (Buddy4Study + NSP)
        │
        ▼
   MongoDB Atlas  ◄── refreshed twice weekly via GitHub Actions
        │
        ▼
Express API + matching engine  (scores + ranks scholarships per user)
        │
        ▼
   React frontend  (Vercel)
```

## 🧠 How the Matching Engine Works

Rather than a single opaque score, each scholarship is evaluated against the logged-in student's profile across four independent factors:

- **Course relevance** — keyword overlap between the student's course and the scholarship's eligibility text
- **Region match** — student's region against the scholarship's stated region
- **CPI eligibility** — a hard filter, not a soft one: scholarships requiring a CPI above the student's are excluded outright
- **Deadline urgency** — closer deadlines score higher
- **Award amount** — normalized to INR across currencies and bucketed into tiers, so results are ranked by real value without one outlier skewing everything

Already-closed scholarships are filtered out before scoring. Full logic lives in `backend/utils/matching.js`.

## 📌 Local Setup

```bash
git clone https://github.com/Manvi1670/Scholarship_finder.git
```

**Frontend:**
```bash
cd ScholarSeek/frontend
npm install
npm run dev
```
Create a `.env` with `VITE_API_URL=http://localhost:3000` (or your deployed backend URL).

**Backend:**
```bash
cd ScholarSeek/backend
npm install
npm start
```
Create a `.env` with `MONGO_URI` and `DB_NAME`.

**Scraper (optional — populates the database):**
```bash
cd ScholarSeek/Scraper
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python refresh_all.py
```
Create a `.env` with the same `MONGO_URI` and `DB_NAME`. A full run scrapes both sources and takes roughly 40–45 minutes.

## 🤖 Automated Refresh

`.github/workflows/scrape.yml` runs the full scraping pipeline automatically every Sunday and Wednesday at 2 AM UTC on GitHub-hosted runners — no manual intervention required to keep scholarship data current. To enable on a fork, add a `MONGO_URI` repository secret under Settings → Secrets and variables → Actions.

## 📷 Screenshots

- [Home page](ScholarSeek/Screenshots/Screenshot_25-6-2025_112120_localhost.jpeg)
- [Register page](ScholarSeek/Screenshots/Screenshot_25-6-2025_112213_localhost.jpeg)
- [Scholarship listing](ScholarSeek/Screenshots/Screenshot_25-6-2025_112410_localhost.jpeg)
- [Scholarship detail](ScholarSeek/Screenshots/Screenshot_25-6-2025_112433_localhost.jpeg)
- [Profile page](ScholarSeek/Screenshots/Screenshot_25-6-2025_11327_localhost.jpeg)

## 👩‍💻 Author

**Manvitha** — [github.com/Manvi1670](https://github.com/Manvi1670)
