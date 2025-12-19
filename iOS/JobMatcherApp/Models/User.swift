//
//  User.swift
//  JobMatcherApp
//
//  User and authentication models
//

import Foundation

struct User: Codable, Identifiable {
    let id: String
    let email: String
    var profile: UserProfile?

    enum CodingKeys: String, CodingKey {
        case id = "user_id"
        case email
        case profile
    }
}

struct UserProfile: Codable {
    var firstName: String
    var lastName: String
    var city: String
    var resumeUrl: String?
    var sectors: [String]
    var jobTypes: [String]
    var yearsExperience: Int
    var skills: [String]
    var salaryMin: Int?
    var phone: String?
    var dailyApplicationLimit: Int
    var notificationPreferences: NotificationPreferences

    enum CodingKeys: String, CodingKey {
        case firstName = "first_name"
        case lastName = "last_name"
        case city
        case resumeUrl = "resume_url"
        case sectors
        case jobTypes = "job_types"
        case yearsExperience = "years_experience"
        case skills
        case salaryMin = "salary_min"
        case phone
        case dailyApplicationLimit = "daily_application_limit"
        case notificationPreferences = "notification_preferences"
    }

    init(
        firstName: String = "",
        lastName: String = "",
        city: String = "",
        resumeUrl: String? = nil,
        sectors: [String] = [],
        jobTypes: [String] = [],
        yearsExperience: Int = 0,
        skills: [String] = [],
        salaryMin: Int? = nil,
        phone: String? = nil,
        dailyApplicationLimit: Int = 10,
        notificationPreferences: NotificationPreferences = NotificationPreferences()
    ) {
        self.firstName = firstName
        self.lastName = lastName
        self.city = city
        self.resumeUrl = resumeUrl
        self.sectors = sectors
        self.jobTypes = jobTypes
        self.yearsExperience = yearsExperience
        self.skills = skills
        self.salaryMin = salaryMin
        self.phone = phone
        self.dailyApplicationLimit = dailyApplicationLimit
        self.notificationPreferences = notificationPreferences
    }
}

struct NotificationPreferences: Codable {
    var enableNewJobs: Bool
    var enableApplicationUpdates: Bool
    var enableWeeklySummary: Bool
    var quietHoursStart: Int // Hour in 24h format (e.g., 22 for 10 PM)
    var quietHoursEnd: Int   // Hour in 24h format (e.g., 8 for 8 AM)

    enum CodingKeys: String, CodingKey {
        case enableNewJobs = "enable_new_jobs"
        case enableApplicationUpdates = "enable_application_updates"
        case enableWeeklySummary = "enable_weekly_summary"
        case quietHoursStart = "quiet_hours_start"
        case quietHoursEnd = "quiet_hours_end"
    }

    init(
        enableNewJobs: Bool = true,
        enableApplicationUpdates: Bool = true,
        enableWeeklySummary: Bool = true,
        quietHoursStart: Int = 22,
        quietHoursEnd: Int = 8
    ) {
        self.enableNewJobs = enableNewJobs
        self.enableApplicationUpdates = enableApplicationUpdates
        self.enableWeeklySummary = enableWeeklySummary
        self.quietHoursStart = quietHoursStart
        self.quietHoursEnd = quietHoursEnd
    }
}

struct AuthResponse: Codable {
    let accessToken: String
    let tokenType: String
    let user: User

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case tokenType = "token_type"
        case user
    }
}

struct LoginRequest: Codable {
    let email: String
    let password: String
}

struct RegisterRequest: Codable {
    let email: String
    let password: String
    let firstName: String
    let lastName: String

    enum CodingKeys: String, CodingKey {
        case email
        case password
        case firstName = "first_name"
        case lastName = "last_name"
    }
}
