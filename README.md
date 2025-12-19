# JobMatcher - Tinder for Startup Jobs

An iOS app that works like "Tinder for startup jobs" - users swipe through job postings from top VC portfolio companies, and the app automatically applies on their behalf.

## Overview

JobMatcher helps job seekers discover and apply to opportunities at top VC-backed startups through an intuitive swipe-based interface. The platform aggregates jobs from leading venture capital firms' portfolio companies and matches them with users based on their preferences and experience.

## Features

### Core Functionality

1. **Tinder-Style Job Discovery**
   - Swipe right to apply, left to reject
   - Smart matching algorithm based on user profile
   - Relevance scoring for each job
   - Undo functionality (5-second window)
   - Visual feedback and smooth animations

2. **Automatic Job Application**
   - Auto-submit applications using user profile
   - AI-generated cover letters
   - Handle custom application questions
   - Support for major ATS platforms (Greenhouse, Lever, Ashby)

3. **Application Pipeline Management**
   - Track applications across 5 statuses
   - Outstanding Questions
   - Applied
   - Interviewing
   - Offered
   - Rejected
   - Timeline visualization
   - Manual status updates
   - Notes and interview tracking

4. **Smart Job Aggregation**
   - Daily scraping of VC portfolio job boards
   - Target VC firms:
     - Sequoia Capital
     - Kleiner Perkins
     - Andreessen Horowitz (a16z)
     - Index Ventures
     - Khosla Ventures
     - First Round Capital
     - Bessemer Venture Partners
     - IVP
     - Greylock Partners
     - Accel
   - Automatic job expiration handling
   - Deduplication

5. **User Profile & Preferences**
   - Comprehensive profile with resume
   - Sector interests (Fintech, AI/ML, etc.)
   - Job type preferences
   - Skills and experience level
   - Location preferences
   - Salary expectations
   - Daily application limits
   - Notification settings

## Project Structure

```
betterlinkedin/
├── iOS/                           # iOS SwiftUI Application
│   ├── JobMatcherApp/
│   │   ├── App/                   # App configuration & main views
│   │   ├── Models/                # Data models
│   │   ├── Views/                 # SwiftUI views
│   │   │   ├── Auth/              # Authentication screens
│   │   │   ├── Swipe/             # Job swiping interface
│   │   │   ├── Pipeline/          # Application tracking
│   │   │   └── Profile/           # User profile & settings
│   │   ├── ViewModels/            # Business logic
│   │   ├── Services/              # API & network layer
│   │   └── Utils/                 # Utilities & helpers
│   └── README.md
│
├── backend/                       # Python FastAPI Backend
│   ├── app/
│   │   ├── api/                   # API endpoints
│   │   ├── models/                # Database models
│   │   ├── services/              # Business logic
│   │   ├── scrapers/              # Web scraping service
│   │   └── core/                  # Configuration
│   ├── alembic/                   # Database migrations
│   ├── requirements.txt
│   └── README.md
│
└── README.md                      # This file
```

## Tech Stack

### iOS App
- **Framework**: SwiftUI (iOS 15+)
- **Language**: Swift 5.7+
- **Architecture**: MVVM
- **Networking**: URLSession with async/await
- **Storage**: Keychain for tokens
- **Minimum iOS**: 15.0

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT tokens
- **Scraping**: Beautiful Soup + Selenium
- **Scheduling**: APScheduler or Celery
- **AI Integration**: OpenAI GPT-4 API (for cover letters)

## Getting Started

### Prerequisites

- **For iOS Development**:
  - macOS with Xcode 14.0+
  - iOS 15.0+ device or simulator

- **For Backend Development**:
  - Python 3.9+
  - PostgreSQL 13+
  - Redis (for caching and job queues)

### iOS App Setup

1. **Create Xcode Project**:
   ```bash
   # Open Xcode and create new iOS App
   # - Name: JobMatcherApp
   # - Interface: SwiftUI
   # - Language: Swift
   # - Deployment Target: iOS 15.0
   ```

2. **Add Source Files**:
   - Copy all files from `iOS/JobMatcherApp/` into your Xcode project
   - Organize into groups matching the folder structure

3. **Configure Backend URL**:
   - Open `Services/APIService.swift`
   - Update `baseURL` to your backend URL

4. **Run**:
   ```bash
   # In Xcode: Cmd + R
   ```

See [iOS/README.md](iOS/README.md) for detailed instructions.

### Backend Setup

1. **Create Virtual Environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials, API keys, etc.
   ```

4. **Setup Database**:
   ```bash
   # Create PostgreSQL database
   createdb jobmatcher

   # Run migrations
   alembic upgrade head
   ```

5. **Run Development Server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

See [backend/README.md](backend/README.md) for detailed instructions.

## Architecture

### Data Flow

1. **Job Scraping** (Backend)
   ```
   Scheduled Job → Scrape VC Sites → Extract Jobs → Store in DB → Calculate Matches
   ```

2. **User Swipes** (iOS → Backend)
   ```
   User Swipes → API Call → Record Decision → Auto-Apply (if right swipe) → Update Pipeline
   ```

3. **Application Tracking** (Backend → iOS)
   ```
   Auto-Apply → Generate Cover Letter → Submit to ATS → Track Status → Notify User
   ```

### Matching Algorithm

Jobs are scored (0-100) based on:
- **Job Type Match** (40%): Does job category match user preferences?
- **Sector Match** (30%): Does industry align with user interests?
- **Location Match** (15%): Is job in preferred location or remote?
- **Experience Match** (15%): Does experience requirement fit user level?

Jobs with score ≥50 are added to user's queue, sorted by relevance.

### Security

- **Authentication**: JWT tokens with refresh mechanism
- **Storage**: Sensitive data encrypted at rest (AES-256)
- **Transport**: HTTPS only for all API calls
- **Passwords**: Bcrypt hashing with salt
- **Tokens**: Stored in iOS Keychain

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user account
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/refresh` - Refresh access token

### Users
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/profile` - Update user profile
- `POST /api/users/resume` - Upload resume

### Jobs
- `GET /api/jobs/queue` - Get personalized job queue
- `POST /api/jobs/swipe` - Record swipe action
- `POST /api/jobs/undo` - Undo last swipe
- `GET /api/jobs/{id}` - Get job details

### Applications
- `GET /api/applications` - Get all applications
- `GET /api/applications?status=applied` - Filter by status
- `PUT /api/applications/{id}/status` - Update status
- `POST /api/applications/{id}/responses` - Submit custom responses
- `PUT /api/applications/{id}/notes` - Add notes

## Deployment

### iOS App
- **TestFlight**: For beta testing
- **App Store**: Production release
- **Requirements**: Apple Developer account ($99/year)

### Backend
- **Recommended**: AWS, Google Cloud, or Railway
- **Components**:
  - API Server (FastAPI)
  - PostgreSQL Database
  - Redis Cache
  - Scheduled Workers (scraping)
  - File Storage (S3 for resumes)

### Environment Variables

Backend `.env` file:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/jobmatcher
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=jobmatcher-resumes
```

## Development Roadmap

### Phase 1: MVP (Current)
- ✅ iOS app with authentication
- ✅ Swipe interface with undo
- ✅ Application pipeline tracking
- ✅ User profile management
- 🚧 Backend API setup
- 🚧 Database models
- 🚧 Web scraping service

### Phase 2: Core Features
- ⬜ Automated job scraping (daily)
- ⬜ Matching algorithm implementation
- ⬜ Auto-application system
- ⬜ AI cover letter generation
- ⬜ Push notifications
- ⬜ Resume upload & parsing

### Phase 3: Advanced Features
- ⬜ Custom application question handling
- ⬜ Analytics dashboard
- ⬜ Interview scheduling integration
- ⬜ Salary negotiation tools
- ⬜ Company research features
- ⬜ Referral tracking

### Phase 4: Scale & Polish
- ⬜ Performance optimization
- ⬜ Advanced search filters
- ⬜ Job recommendations ML model
- ⬜ Social features (share jobs)
- ⬜ Chrome extension for manual adds
- ⬜ Email integration

## Contributing

This is a private project. For questions or issues, please contact the maintainers.

## Legal & Compliance

### Web Scraping
- Respect `robots.txt`
- Rate limiting (1-2 req/sec)
- User-Agent rotation
- For personal use only

### Privacy
- GDPR compliant
- User data export capability
- Right to deletion
- Transparent data usage

### Disclaimer
This tool automates job applications. Users should:
- Review auto-generated content
- Ensure applications are accurate
- Respect daily application limits
- Use responsibly

## License

Copyright © 2024 JobMatcher. All rights reserved.

## Contact

For questions or support, please open an issue on GitHub.
