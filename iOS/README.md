# JobMatcher iOS App

A Tinder-style job matching app that helps users discover and apply to jobs from top VC-backed startups.

## Features

### 1. Authentication
- User registration and login
- Secure token storage with Keychain
- JWT-based authentication

### 2. Swipe Interface
- Tinder-style card swiping for job discovery
- Left swipe to reject, right swipe to apply
- Undo functionality (5-second window)
- Visual feedback and animations
- Relevance score display
- Pull to refresh for new jobs

### 3. Application Pipeline
- Track all applications across 5 statuses:
  - Outstanding Questions
  - Applied
  - Interviewing
  - Offered
  - Rejected
- Detailed application view
- Manual status updates
- Timeline tracking
- Expired job indicators

### 4. User Profile
- Complete profile management
- Sector and job type preferences
- Skills management
- Experience level
- Salary expectations
- Notification preferences
- Daily application limits
- Resume upload

## Project Structure

```
iOS/JobMatcherApp/
├── App/
│   ├── JobMatcherApp.swift        # Main app entry point
│   └── MainTabView.swift          # Tab navigation container
├── Models/
│   ├── User.swift                 # User and auth models
│   ├── Job.swift                  # Job posting models
│   └── Application.swift          # Application tracking models
├── Views/
│   ├── Auth/
│   │   ├── AuthenticationView.swift
│   │   ├── LoginView.swift
│   │   └── RegisterView.swift
│   ├── Swipe/
│   │   ├── SwipeView.swift
│   │   └── JobCardView.swift
│   ├── Pipeline/
│   │   ├── PipelineView.swift
│   │   └── ApplicationDetailView.swift
│   └── Profile/
│       ├── ProfileView.swift
│       └── MultiSelectView.swift
├── ViewModels/
│   ├── AuthViewModel.swift
│   ├── SwipeViewModel.swift
│   ├── PipelineViewModel.swift
│   └── ProfileViewModel.swift
├── Services/
│   └── APIService.swift           # Backend API communication
└── Utils/
    └── KeychainHelper.swift       # Secure token storage
```

## Requirements

- iOS 15.0+
- Xcode 14.0+
- Swift 5.7+

## Setup

### 1. Create Xcode Project

1. Open Xcode
2. Create a new iOS App project
3. Name it "JobMatcherApp"
4. Select SwiftUI as the interface
5. Select Swift as the language
6. Set deployment target to iOS 15.0

### 2. Add Source Files

Copy all files from this directory structure into your Xcode project:

1. In Xcode, right-click on the project navigator
2. Select "Add Files to JobMatcherApp"
3. Navigate to each folder and add the corresponding Swift files
4. Ensure "Copy items if needed" is checked
5. Ensure "Create groups" is selected

### 3. Configure Backend URL

Update the `baseURL` in `Services/APIService.swift`:

```swift
private let baseURL = "http://your-backend-url.com/api"
```

For local development:
- iOS Simulator: `http://localhost:8000/api`
- Physical device: `http://YOUR_COMPUTER_IP:8000/api`

### 4. Update Info.plist

Add the following permissions:

```xml
<key>NSPhotoLibraryUsageDescription</key>
<string>We need access to your photo library to upload your resume</string>

<key>NSCameraUsageDescription</key>
<string>We need access to your camera to take photos of documents</string>
```

For local HTTP connections (development only):

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

### 5. Run the App

1. Select your target device or simulator
2. Press Cmd+R to build and run
3. The app will launch with the login screen

## API Integration

The app expects the following API endpoints:

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### User
- `GET /api/users/me` - Get current user
- `PUT /api/users/profile` - Update user profile

### Jobs
- `GET /api/jobs/queue?limit=20` - Get job queue
- `POST /api/jobs/swipe` - Record swipe action
- `POST /api/jobs/undo` - Undo last swipe

### Applications
- `GET /api/applications?status=applied` - Get applications
- `PUT /api/applications/{id}/status` - Update application status
- `POST /api/applications/{id}/responses` - Submit custom question responses

## Key Features Explained

### Swipe Gestures

The `JobCardView` implements drag gestures:
- Drag threshold: 150 points
- Visual indicators appear at 20 points
- Cards animate off-screen on successful swipe
- Spring animation returns card to center on cancelled swipe

### Undo Functionality

- Shows for 5 seconds after each swipe
- Only allows undoing the most recent action
- Automatically hides after timeout
- Restores job to current position in queue

### State Management

The app uses the MVVM pattern:
- **Models**: Data structures (User, Job, Application)
- **Views**: SwiftUI views for UI
- **ViewModels**: Business logic and state management (@MainActor for thread safety)

### Security

- JWT tokens stored in iOS Keychain
- All API requests include Authorization header
- Automatic logout on 401 responses

## Customization

### Colors and Styling

Update colors in views:
- Primary action color: `.blue`
- Apply button: `.green`
- Reject button: `.red`

### Job Relevance Scoring

Customize score colors in `JobCardView.scoreColor()`:
- 80-100: Green (Excellent match)
- 60-79: Orange (Good match)
- 0-59: Gray (Fair match)

### Application Limits

Default daily limit: 10 applications
Users can adjust between 1-50 in Profile settings

## Testing

The app includes SwiftUI previews for all major components. To view:

1. Open any view file
2. Press Cmd+Option+Enter to show canvas
3. Click "Resume" if preview is paused

## Troubleshooting

### Cannot connect to backend

- Verify backend is running
- Check `baseURL` in `APIService.swift`
- Ensure Info.plist allows HTTP (for local development)
- On physical device, use computer's IP address

### Keychain errors

- Reset simulator: Device > Erase All Content and Settings
- On device: Delete app and reinstall

### Build errors

- Clean build folder: Product > Clean Build Folder (Cmd+Shift+K)
- Delete derived data: ~/Library/Developer/Xcode/DerivedData
- Restart Xcode

## Next Steps

1. Implement resume file upload
2. Add push notifications
3. Implement custom question forms for applications
4. Add analytics dashboard
5. Implement AI-generated cover letters
6. Add deep linking for application platforms

## License

Copyright © 2024 JobMatcher. All rights reserved.
