//
//  Application.swift
//  JobMatcherApp
//
//  Job application tracking models
//

import Foundation

enum ApplicationStatus: String, Codable, CaseIterable {
    case outstanding = "outstanding"
    case applied = "applied"
    case interviewing = "interviewing"
    case offered = "offered"
    case rejected = "rejected"

    var displayName: String {
        switch self {
        case .outstanding:
            return "Outstanding Questions"
        case .applied:
            return "Applied"
        case .interviewing:
            return "Interviewing"
        case .offered:
            return "Offered"
        case .rejected:
            return "Rejected"
        }
    }

    var icon: String {
        switch self {
        case .outstanding:
            return "questionmark.circle.fill"
        case .applied:
            return "paperplane.fill"
        case .interviewing:
            return "person.2.fill"
        case .offered:
            return "star.fill"
        case .rejected:
            return "xmark.circle.fill"
        }
    }
}

struct Application: Codable, Identifiable {
    let id: String
    let userId: String
    let job: Job
    var status: ApplicationStatus
    let dateSwiped: Date
    var dateApplied: Date?
    var customResponses: [CustomResponse]?
    var coverLetter: String?
    var notes: String?
    var interviewStage: String?
    var offerDetails: OfferDetails?

    enum CodingKeys: String, CodingKey {
        case id = "application_id"
        case userId = "user_id"
        case job
        case status
        case dateSwiped = "date_swiped"
        case dateApplied = "date_applied"
        case customResponses = "custom_responses"
        case coverLetter = "cover_letter"
        case notes
        case interviewStage = "interview_stage"
        case offerDetails = "offer_details"
    }

    var isExpired: Bool {
        !job.isActive
    }
}

struct CustomResponse: Codable, Identifiable {
    let id: String
    let questionId: String
    var response: String

    enum CodingKeys: String, CodingKey {
        case id
        case questionId = "question_id"
        case response
    }
}

struct OfferDetails: Codable {
    var salary: Int?
    var startDate: Date?
    var equity: String?
    var benefits: String?
    var otherDetails: String?

    enum CodingKeys: String, CodingKey {
        case salary
        case startDate = "start_date"
        case equity
        case benefits
        case otherDetails = "other_details"
    }
}

struct SwipeAction: Codable {
    let jobId: String
    let action: SwipeDirection
    let timestamp: Date

    enum CodingKeys: String, CodingKey {
        case jobId = "job_id"
        case action
        case timestamp
    }
}

enum SwipeDirection: String, Codable {
    case left = "left"
    case right = "right"
}
