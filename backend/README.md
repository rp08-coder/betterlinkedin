# JobMatcher Backend API

FastAPI backend for the JobMatcher iOS app - handles authentication, job aggregation, matching, and application tracking.

## Features

- **User Authentication**: JWT-based authentication with secure password hashing
- **Job Aggregation**: Web scraping of VC firm portfolio job boards
- **Smart Matching**: Algorithm to match jobs with user preferences
- **Application Tracking**: Pipeline management across 5 status stages
- **Swipe Management**: Track swipes with undo functionality
- **Profile Management**: Comprehensive user profiles with preferences

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with async SQLAlchemy
- **Authentication**: JWT tokens with bcrypt password hashing
- **Web Scraping**: Beautiful Soup + aiohttp
- **Migrations**: Alembic
- **Python**: 3.9+

## Project Structure

```
backend/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   ├── env.py                  # Migration environment
│   └── script.py.mako          # Migration template
├── app/
│   ├── api/                    # API layer
│   │   ├── endpoints/          # API endpoints
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── users.py        # User/profile endpoints
│   │   │   ├── jobs.py         # Job/swipe endpoints
│   │   │   └── applications.py # Application endpoints
│   │   └── dependencies.py     # Shared dependencies
│   ├── core/                   # Core configuration
│   │   ├── config.py           # Settings
│   │   ├── database.py         # Database setup
│   │   └── security.py         # Auth utilities
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py             # User model
│   │   ├── job.py              # Job models
│   │   └── application.py      # Application models
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py             # User schemas
│   │   ├── job.py              # Job schemas
│   │   └── application.py      # Application schemas
│   ├── scrapers/               # Web scraping
│   │   ├── base_scraper.py     # Base scraper class
│   │   └── example_scraper.py  # Example implementation
│   ├── services/               # Business logic (future)
│   └── main.py                 # FastAPI app
├── tests/                      # Tests
├── .env.example                # Environment template
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## Setup

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 13 or higher
- Redis (optional, for caching)

### 1. Clone and Navigate

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=postgresql+asyncpg://jobmatcher:password@localhost:5432/jobmatcher

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# OpenAI (optional, for cover letters)
OPENAI_API_KEY=sk-your-key-here

# AWS (optional, for resume storage)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET=jobmatcher-resumes
```

### 5. Create Database

```bash
# Using psql
psql -U postgres
CREATE DATABASE jobmatcher;
CREATE USER jobmatcher WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE jobmatcher TO jobmatcher;
\q

# Or using createdb
createdb -U postgres jobmatcher
```

### 6. Run Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 7. Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "user_id": "uuid",
    "email": "user@example.com",
    "profile": null
  }
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

### Users

#### Get Current User
```http
GET /api/users/me
Authorization: Bearer {token}
```

#### Update Profile
```http
PUT /api/users/profile
Authorization: Bearer {token}
Content-Type: application/json

{
  "city": "San Francisco",
  "sectors": ["Fintech", "AI/ML"],
  "job_types": ["Software Engineer", "Product Manager"],
  "skills": ["Python", "Swift", "React"],
  "years_experience": 5,
  "salary_min": 150000
}
```

### Jobs

#### Get Job Queue
```http
GET /api/jobs/queue?limit=20
Authorization: Bearer {token}
```

#### Swipe on Job
```http
POST /api/jobs/swipe
Authorization: Bearer {token}
Content-Type: application/json

{
  "job_id": "uuid",
  "action": "right",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Undo Last Swipe
```http
POST /api/jobs/undo
Authorization: Bearer {token}
```

### Applications

#### Get All Applications
```http
GET /api/applications
Authorization: Bearer {token}
```

#### Filter by Status
```http
GET /api/applications?status=applied
Authorization: Bearer {token}
```

#### Update Application Status
```http
PUT /api/applications/{application_id}/status
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "interviewing"
}
```

## Database Models

### User

- **user_id**: UUID primary key
- **email**: Unique email address
- **password_hash**: Bcrypt hashed password
- **first_name**, **last_name**: User name
- **city**: Current city
- **phone**: Optional phone number
- **resume_url**: Link to uploaded resume
- **sectors**: Array of preferred sectors
- **job_types**: Array of preferred job types
- **skills**: Array of skills
- **years_experience**: Years of experience
- **salary_min**: Minimum salary expectation
- **rejected_job_urls**: Array of rejected job URLs
- **daily_application_limit**: Max applications per day
- **notification_preferences**: JSON notification settings

### Job

- **job_id**: UUID primary key
- **source_url**: Original job posting URL (unique)
- **vc_firm**: VC firm name
- **company_name**: Company name
- **company_logo_url**: Optional logo URL
- **job_title**: Job title
- **description**: Full description
- **requirements**: Job requirements
- **job_category**: Category (Engineering, Product, etc.)
- **sector**: Industry sector
- **location**: Job location
- **is_active**: Whether job is still active
- **application_url**: Where to apply
- **application_platform**: ATS platform name
- **custom_questions**: Optional custom questions

### JobQueue

- **queue_id**: UUID primary key
- **user_id**: Foreign key to User
- **job_id**: Foreign key to Job
- **relevance_score**: Matching score (0-100)
- **shown**: Whether user has seen this job
- **date_added**: When added to queue

### Application

- **application_id**: UUID primary key
- **user_id**: Foreign key to User
- **job_id**: Foreign key to Job
- **status**: Enum (outstanding, applied, interviewing, offered, rejected)
- **date_swiped**: When user swiped right
- **date_applied**: When application was submitted
- **custom_responses**: Responses to custom questions
- **cover_letter**: Auto-generated cover letter
- **notes**: User notes
- **interview_stage**: Current interview stage
- **offer_details**: Offer information

## Web Scraping

### Creating a New Scraper

1. Create a new file in `app/scrapers/` (e.g., `sequoia_scraper.py`)
2. Extend `BaseScraper` class
3. Implement two methods:
   - `get_portfolio_companies()`: Extract job URLs
   - `scrape_job()`: Extract job details

Example:

```python
from app.scrapers.base_scraper import BaseScraper

class SequoiaScraper(BaseScraper):
    def __init__(self):
        super().__init__("Sequoia Capital")
        self.portfolio_url = "https://www.sequoiacap.com/jobs"

    async def get_portfolio_companies(self, session):
        html = await self.fetch_page(self.portfolio_url, session)
        soup = self.parse_html(html)
        # Extract job URLs...
        return job_urls

    async def scrape_job(self, url, session):
        html = await self.fetch_page(url, session)
        soup = self.parse_html(html)
        # Extract job details...
        return job_data
```

### Running Scrapers

```python
from app.scrapers.sequoia_scraper import SequoiaScraper

scraper = SequoiaScraper()
jobs = await scraper.scrape_all_jobs()
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## Database Migrations

### Create New Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade {revision_id}

# Downgrade one revision
alembic downgrade -1
```

### View Migration History

```bash
alembic history
alembic current
```

## Development

### Code Style

Format code with Black:

```bash
black app/
```

Lint with flake8:

```bash
flake8 app/
```

Type check with mypy:

```bash
mypy app/
```

### Database Shell

```bash
# PostgreSQL shell
psql -U jobmatcher -d jobmatcher

# Useful commands
\dt                    # List tables
\d users              # Describe users table
\d+ applications      # Detailed description
SELECT * FROM users;  # Query
```

## Deployment

### Production Setup

1. Set environment to production:
   ```env
   ENVIRONMENT=production
   DEBUG=False
   ```

2. Use a production ASGI server:
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. Set up HTTPS with nginx or similar

4. Use production database with connection pooling

5. Set up Redis for caching

6. Configure log aggregation

### Deployment Platforms

- **Railway**: Easiest deployment, automatic PostgreSQL
- **Heroku**: Simple with Heroku Postgres
- **AWS**: EC2 + RDS PostgreSQL
- **Google Cloud**: Cloud Run + Cloud SQL
- **DigitalOcean**: App Platform or Droplet

### Environment Variables for Production

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
SECRET_KEY=generate-a-strong-random-key
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=["https://yourdomain.com"]
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready

# Restart PostgreSQL
sudo service postgresql restart

# Check connection
psql -U jobmatcher -d jobmatcher
```

### Migration Issues

```bash
# Reset database (WARNING: deletes all data)
alembic downgrade base
alembic upgrade head

# Or drop and recreate
dropdb jobmatcher
createdb jobmatcher
alembic upgrade head
```

### Import Errors

```bash
# Ensure you're in virtual environment
which python  # Should point to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

## License

Copyright © 2024 JobMatcher. All rights reserved.
