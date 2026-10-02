# TruthLens — AI-Powered Fake News Detection Platform

TruthLens is an enterprise-grade Fake News Detection and Fact-Checking Platform that blends natural language processing, multi-model ensemble machine learning, SQLite FTS5 full-text corpus indexing, domain credibility verification, and a modern React (Vite) single-page application.

---

## 🚀 Key Features & Capabilities

- **Hybrid Detection Pipeline**:
  - **FTS5 Corpus Matching**: Sub-millisecond full-text search against 14,000+ verified benchmark news statements (`train.csv`, `valid.csv`, `test.csv`, and LIAR dataset).
  - **Ensemble Machine Learning**: Integrates multiple classifiers (Logistic Regression, Naive Bayes, Decision Trees, Linear SVM, SGD, Random Forest) with TF-IDF n-gram vectorization.
  - **Forensic Evidence & Explainability**: Structured evidence grids with "Why Real vs. Why Fake" factor breakdowns, journalistic source attribution, factual entity density, and emotional clickbait indicators.
  - **Domain & URL Analysis**: SSRF-protected article scraper, domain reputation rating, and SSL trust evaluation.
  - **Exportable Fact-Check Certificates**: Instant, printable verification reports for users and journalists.

- **Unified React SPA Frontend**:
  - **Public News Detector (`facknews.local`)**: Live statement & URL verification, sentiment analysis gauges, objectivity meters, contact enquiry form, and real-time evidence cards.
  - **Admin Control Portal (`portal.appur` / `portal.facknews.local`)**: Secure token-based authentication, interactive detection statistics, human-in-the-loop review queue, and CMS management.

- **Domain-Based Routing**:
  - `facknews.local` (or `APP_URL`): Directs visitors to the public detector and about/contact portal.
  - `portal.appur` / `portal.facknews.local` (or `PORTAL_URL`): Directs users to the admin login, or straight to the admin dashboard if already authenticated.

---

## 📂 Architecture Overview

```
/var/www/facknews/
├── apps/
│   ├── authentication/        # Custom User model, token auth, admin seeder
│   │   ├── management/commands/seed_admin.py
│   │   └── views.py
│   ├── cms/                   # CMS viewsets (Enquiries, NewsAndUpdate, Sliders, Teams, etc.)
│   │   ├── models.py
│   │   └── views.py
│   └── core/                  # Core SPA index_view, permissions, pagination
│       └── views.py
│
├── detection/                 # Core Detection Engine & Microservices
│   ├── models.py              # IndexedNews, DetectionLog, Article
│   ├── views.py               # /api/detect/, /api/articles/, /api/review-queue/, /api/history/
│   ├── services/
│   │   ├── detector.py        # FakeNewsDetector orchestrator
│   │   ├── matcher.py         # SQLite FTS5 corpus matcher
│   │   ├── scoring.py         # Calibrated confidence & ground-truth scorer
│   │   ├── domain_analyzer.py # URL content extractor & domain trust
│   │   └── ensemble.py        # Multi-model prediction combiner
│   └── management/commands/
│       └── index_dataset.py   # Ingests train/test/valid CSVs into SQLite FTS5 index
│
├── FakeNewsDetect/            # Django Project Configuration
│   ├── settings.py            # Unified settings, static, CORS, templates
│   ├── urls.py                # Central URL routing
│   └── wsgi.py                # WSGI entrypoint for Gunicorn
│
├── frontend/                  # Modern React + Vite Single-Page Application
│   ├── src/                   # React components, pages, contexts, styling
│   ├── dist/                  # Production build served directly by Apache/Django
│   ├── package.json
│   └── vite.config.js
│
├── ml_models/                 # Serialized model pickles
├── train_model.py             # Scikit-learn TF-IDF + Logistic Regression training pipeline
├── final_model.sav            # Pre-trained production classification model
├── train.csv, test.csv, valid.csv  # Benchmark news datasets (14,000+ labeled statements)
├── manage.py                  # Django CLI entrypoint (auto-activates .venv)
└── requirements.txt           # Python dependency requirements
```

---

## 🛠️ Complete Terminal Commands Guide

All primary administrative tasks can be run directly from the project root:
```bash
cd /var/www/facknews
```

---

### 1. Environment & Dependencies

#### Activate the Virtual Environment:
```bash
# Linux / macOS
source .venv/bin/activate
```

#### Install / Update Dependencies:
```bash
# Using uv (fastest)
uv pip install -r requirements.txt

# Or using standard pip
pip install -r requirements.txt
```

---

### 2. Database Migrations

#### Create New Migrations (when modifying models):
```bash
python manage.py makemigrations
```

#### Apply All Pending Migrations:
```bash
python manage.py migrate
```

#### Check Migration Status:
```bash
python manage.py showmigrations
```

---

### 3. Model Training & Dataset Indexing

#### Train the Fake News ML Model from Scratch:
```bash
python train_model.py
```
> Reads `train.csv` and `test.csv`, extracts TF-IDF n-gram features, trains a Logistic Regression pipeline, evaluates precision/recall/F1 metrics, and serializes the model to `final_model.sav`.

#### Index Benchmark Datasets into SQLite FTS5:
```bash
python manage.py index_dataset
```
> Parses `train.csv`, `valid.csv`, `test.csv`, and LIAR dataset files. Ingests and SHA-256 deduplicates 14,000+ ground-truth statements into the `IndexedNews` table and SQLite FTS5 virtual table for instantaneous sub-millisecond lookups.

---

### 4. Admin Seeder & Superuser Creation

#### Seed the Default Admin Account:
```bash
python manage.py seed_admin
```
- **Email**: `pashupati@python.py`
- **Password**: `Forgot911!`
- **Role**: `admin`

#### Create a Custom Django Superuser:
```bash
python manage.py createsuperuser
```

---

### 5. Running the Application Server

#### Option A: Running as Background Service (Default & Recommended)
The server runs continuously via systemd user service on `127.0.0.1:8000`, reverse-proxied by Apache on Port 80:
```bash
# Check service status
systemctl --user status facknews

# Restart background server
systemctl --user restart facknews

# Stop background server
systemctl --user stop facknews

# Start background server
systemctl --user start facknews

# View live background server logs
journalctl --user-unit=facknews -f
```

#### Option B: Running Interactively in Terminal
If you want to view real-time request logs directly in your terminal, stop the background service first to release port 8000:
```bash
systemctl --user stop facknews
python manage.py runserver 127.0.0.1:8000

# Or using the built-in terminal alias:
runserver
```

#### Option C: Production Gunicorn Runner:
```bash
gunicorn FakeNewsDetect.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120
```

---

### 6. Apache Web Server Configuration

Apache is configured as a high-performance reverse proxy that serves static assets directly from `frontend/dist` and proxies application traffic to Django:

```bash
# Test Apache configuration syntax
apache2ctl -t

# Reload Apache without downtime
systemctl reload apache2

# Restart Apache service
sudo systemctl restart apache2
```

Configuration file: `/etc/apache2/sites-available/facknews.local.conf`

---

### 7. Frontend Development (React + Vite)

The frontend lives in the `frontend/` directory.

```bash
cd /var/www/facknews/frontend

# Install node dependencies
npm install

# Start Vite live-reload dev server (runs on http://localhost:5173)
npm run dev

# Build production bundle (compiles into frontend/dist)
npm run build
```

---

### 8. Running the Automated Test Suite

TruthLens includes comprehensive automated tests covering authentication, CMS enquiries, ML prediction pipelines, and REST APIs:

```bash
# Run all tests
python manage.py test

# Run tests with detailed verbose output
python manage.py test -v 2

# Run authentication app tests
python manage.py test apps.authentication

# Run CMS enquiries tests
python manage.py test apps.cms

# Run detection engine tests
python manage.py test detection
```

---

## 🔑 Default Credentials

| Portal | Email | Password | Role |
| :--- | :--- | :--- | :--- |
| **Admin Portal** | `pashupati@python.py` | `Forgot911!` | Super Administrator |
| **Admin Portal (Legacy)** | `admin@gmail.com` | `admin123` | Administrator |

---

## 🌐 URLs & Access Points

| Service | URL | Description |
| :--- | :--- | :--- |
| **Public Detector** | [http://facknews.local](http://facknews.local) | News statement verification, URL detector, About & Contact Us |
| **Admin Portal** | [http://portal.facknews.local](http://portal.facknews.local) | Administrator login & TruthLens monitoring dashboard |
| **Alt Portal Domain** | [http://portal.appur](http://portal.appur) | Secondary portal domain configured in `.env` |
| **Django Admin** | [http://facknews.local/admin/](http://facknews.local/admin/) | Django built-in model administration |

---

## 📡 API Endpoints Reference

### 1. Detection APIs
- **`POST /api/detect/`**: Verify text statement (JSON: `{"content": "..."}`).
- **`POST /api/detect/url/`**: Verify web article from URL (JSON: `{"url": "https://..."}`).
- **`POST /api/source/check/`**: Evaluate domain credibility & historical fake rate.
- **`POST /detect/`**: Legacy backward-compatible detection endpoint.

### 2. Monitoring, Models & Training APIs
- **`GET /api/system/stats/`**: Database size, total detections, indexed news count, and retention policy.
- **`GET /api/models/summary/`**: Full inventory of all 6 ML classifiers, individual sample counts, real/fake counts, and accuracy metrics.
- **`GET /api/models/data/?page=1&page_size=15&search=...&label=...&source=...`**: Server-side paginated and filtered benchmark statements with dynamic real/fake totals.
- **`POST /api/models/train/`**: Launches asynchronous model training pipeline (`train_model.py`) in background worker thread.
- **`GET /api/models/train/status/?since=0`**: Polls live training status, elapsed running time stopwatch, and stdout console stream.
- **`GET /api/history/`**: Paginated detection audit log.
- **`GET /api/review-queue/`**: Borderline detections awaiting human review.
- **`POST /api/detections/<id>/review/`**: Submit human reviewer override verdict.
- **`GET /api/articles/`**: Curated articles repository list.
- **`POST /api/articles/`**: Create new curated article.
- **`PUT /api/articles/<id>/`**: Edit article.
- **`DELETE /api/articles/<id>/`**: Delete article.

### 3. CMS & Public APIs
- **`POST /api/v1/cms/enquiries/`**: Anonymous contact enquiry form submission.
- **`GET /api/v1/cms/enquiries/`**: Admin enquiry management view.
- **`POST /api/v1/auth/login/`**: Token-based administrator login.
- **`GET /api/v1/auth/me/`**: Current authenticated user profile.

---

## 🛡️ License
TruthLens is developed and maintained under the MIT License.
