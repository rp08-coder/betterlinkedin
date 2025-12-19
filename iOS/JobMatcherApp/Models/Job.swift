//
//  Job.swift
//  JobMatcherApp
//
//  Job posting models
//

import Foundation

struct Job: Codable, Identifiable {
    let id: String
    let sourceUrl: String
    let companyName: String
    let companyLogoUrl: String?
    let jobTitle: String
    let description: String
    let requirements: String
    let jobCategory: String
    let sector: String
    let location: String
    let datePosted: Date?
    let isActive: Bool
    let applicationUrl: String
    let applicationPlatform: String
    let customQuestions: [CustomQuestion]?
    var relevanceScore: Int?

    enum CodingKeys: String, CodingKey {
        case id = "job_id"
        case sourceUrl = "source_url"
        case companyName = "company_name"
        case companyLogoUrl = "company_logo_url"
        case jobTitle = "job_title"
        case description
        case requirements
        case jobCategory = "job_category"
        case sector
        case location
        case datePosted = "date_posted"
        case isActive = "is_active"
        case applicationUrl = "application_url"
        case applicationPlatform = "application_platform"
        case customQuestions = "custom_questions"
        case relevanceScore = "relevance_score"
    }

    var shortDescription: String {
        if description.count <= 200 {
            return description
        }
        let index = description.index(description.startIndex, offsetBy: 200)
        return String(description[..<index]) + "..."
    }

    var requirementsList: [String] {
        requirements
            .components(separatedBy: "\n")
            .filter { !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
            .prefix(5)
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
    }
}

struct CustomQuestion: Codable, Identifiable {
    let id: String
    let question: String
    let questionType: String
    let required: Bool

    enum CodingKeys: String, CodingKey {
        case id
        case question
        case questionType = "question_type"
        case required
    }
}

struct JobQueue: Codable {
    let queueId: String
    let job: Job
    let relevanceScore: Int
    let dateAdded: Date

    enum CodingKeys: String, CodingKey {
        case queueId = "queue_id"
        case job
        case relevanceScore = "relevance_score"
        case dateAdded = "date_added"
    }
}
