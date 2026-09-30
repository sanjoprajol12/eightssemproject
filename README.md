# TruthLens — AI-Powered Fake News Detection System

TruthLens is an enterprise-grade Fake News Detection and Fact-Checking Platform that blends natural language processing, multi-model ensemble machine learning, full-text corpus indexing (FTS5), domain reputation analysis, and an interactive dark glassmorphic web dashboard.

---

## 🚀 Key Features & Capabilities

- **Hybrid Detection & Free AI Reasoning Pipeline**:
  - **FTS5 Corpus Matching**: Sub-millisecond full-text search against verified real and fake news corpora.
  - **Ensemble Machine Learning**: Integrates multiple classifiers including Logistic Regression, Naive Bayes, Decision Trees, Linear SVM, SGD, and Random Forest.
  - **Why It Is Real vs. Why It Is Fake (Deep Analysis)**: Generates dual-factor structured evidence grids highlighting journalistic attributions, factual entity density, clickbait triggers, and emotional manipulation patterns.
  - **Free AI Reasoning Engine**: Built-in zero-shot neural reasoner with NLTK VADER sentiment analysis, objectivity scoring, and automatic fallback support for free cloud LLM inference (Groq/HuggingFace).
  - **Domain & URL Analysis**: SSRF-protected URL content scraper, domain reputation scoring, and SSL/TLD trust evaluation.
  - **Exportable Fact-Check Audit**: Print-ready, branded fact-check verification certificates.

- **Unified Glassmorphism UI (Min-UI Design System)**:
  - Deep navy and indigo palette (`#080c14`, `#6366f1`, `#06b6d4`, `#10b981`, `#f43f5e`).
  - **Public Detector (`/`)**: Asynchronous text & URL verification with animated confidence gauges, AI executive summary, dual Why Real / Why Fake cards, objectivity and emotional charge meters, and print-ready fact-check export.
  - **Admin Authentication (`/login/`, `/register/`)**: Secure session-based authentication with animated feedback.
  - **Interactive Admin Dashboard (`/dashboard/`)**: Pure vanilla JS & CSS, overview metric cards, recent articles table, quick detector, complete Article CRUD with image uploads, system telemetry panel, in-place profile management, and a dedicated **Detection Logs & Audit Trail** browser with search and inspection modal.

- **Enterprise Security**:
  - Constant-time password validation & Django `pbkdf2_sha256` password hashing.
  - Automatic, seamless migration of legacy plaintext admin credentials to salted PBKDF2 hashes upon login.
  - CSRF cookie validation across all mutating API endpoints (`POST`, `PUT`, `DELETE`).

---

## 📂 Architecture Overview

```
Fake_News_Detection/
├── accounts/                  # Authentication, Admin & Article Management
│   ├── models.py             # Admin and Article models
│   ├── views.py              # Login, register, profile_api, article CRUD, dashboard views
│   ├── templates/            # Modern dark glassmorphic templates
│   │   ├── index.html        # Public detector landing page
│   │   ├── login.html        # Admin login page
│   │   ├── register.html     # Admin registration page
│   │   └── dashboard.html    # Full vanilla JS admin control room
│   └── tests.py              # Automated auth, profile, and article CRUD test suite
│
├── detection/                 # Core Detection Engine & Microservices
│   ├── models.py             # IndexedNews, DetectionLog
│   ├── views.py              # /api/detect/, /detect/, /api/detect/url/, /api/system/stats/
│   ├── services/
│   │   ├── detector.py       # High-level FakeNewsDetector orchestrator
│   │   ├── matcher.py        # FTS5 SQLite indexed corpus matcher
│   │   ├── ensemble.py       # Multi-model prediction combiner
│   │   ├── scraper.py        # Safe URL content extractor
│   │   └── scoring.py        # Confidence calibration & verdict calculation
│   └── tests.py              # Detection API and validation tests
│
├── FakeNewsDetect/            # Django Project Configuration
│   ├── settings.py           # Database, template priority, static & media configs
│   └── urls.py               # Root URL router
│
├── front.py                   # Complementary Flask detector
├── train_model.py             # Model training & serialization pipeline
├── final_model.sav            # Trained scikit-learn TF-IDF + Logistic Regression model
└── manage.py                  # Django CLI entrypoint
```

---

## 🛠️ Getting Started

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- Virtual environment (`venv`)

### 2. Setup & Installation

Activate the virtual environment and install dependencies:

```bash
# On Windows PowerShell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Run Database Migrations

```bash
python manage.py migrate
```

### 4. Start the Django Server

```bash
python manage.py runserver 127.0.0.1:8000
```

Open your browser to:
- **Public Detector**: `http://127.0.0.1:8000/`
- **Admin Login**: `http://127.0.0.1:8000/login/`
- **Admin Dashboard**: `http://127.0.0.1:8000/dashboard/`

*(Optional) To run the lightweight Flask application:*
```bash
python front.py
# Runs on http://127.0.0.1:5000/
```

---

## 🔑 Default Credentials

| Email | Password | Role |
| :--- | :--- | :--- |
| `admin@gmail.com` | `admin123` | Default Admin |
| `pashupatisah35@gmail.com` | `123456789` | Fact-Check Admin |

*(Note: Passwords are automatically upgraded to `pbkdf2_sha256` hashing upon initial login).*

---

## 📡 API Reference

### 1. Public / Client Detection
- **`POST /detect/`** (or **`POST /api/detect/`**)
  - **Body** (JSON or Form): `{"content": "News text or headline to analyze..."}`
  - **Response**:
    ```json
    {
      "result": "Real News | Fake News | Inconclusive",
      "confidence": 95.5,
      "source": "FTS5 Indexed Corpus Match | ML Ensemble Pipeline",
      "models": {
        "predictions": {
          "logistic_regression": "Real News",
          "naive_bayes": "Real News",
          "random_forest": "Real News"
        }
      },
      "evidence": {
        "matches": [...],
        "match_count": 3
      },
      "explanation": ["Matched known verified article in corpus..."]
    }
    ```

- **`POST /api/detect/url/`**
  - **Body**: `{"url": "https://reuters.com/world/article-headline"}`
  - **Response**: Full credibility report including domain reputation and extracted content score.

### 2. Telemetry & Articles
- **`GET /api/system/stats/`**: Returns database size, total detections, indexed articles count, and retention policy.
- **`GET /api/articles/`**: Returns all news articles (JSON).
- **`POST /api/articles/`**: Creates a new article (requires authenticated session & CSRF).
- **`GET /api/articles/<id>/`**: Fetches single article details.
- **`PUT /api/articles/<id>/`**: Updates an existing article.
- **`DELETE /api/articles/<id>/`**: Deletes an article and cleans up stored image files.
- **`GET /api/profile/`**: Fetches current admin details.
- **`POST /api/profile/`**: Updates current admin profile in-place.

---

## 🧪 Automated Testing

TruthLens includes an automated test suite verifying all critical paths:

```bash
# Run the complete test suite
python manage.py test

# Run accounts tests only
python manage.py test accounts

# Run detection API tests only
python manage.py test detection
```

---

## 🛡️ License
TruthLens is developed and maintained under the MIT License.
