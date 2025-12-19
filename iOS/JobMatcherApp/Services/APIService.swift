//
//  APIService.swift
//  JobMatcherApp
//
//  API service for backend communication
//

import Foundation

enum APIError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case unauthorized
    case decodingError
    case serverError(String)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .invalidResponse:
            return "Invalid response from server"
        case .unauthorized:
            return "Unauthorized. Please log in again."
        case .decodingError:
            return "Failed to decode response"
        case .serverError(let message):
            return message
        }
    }
}

class APIService {
    static let shared = APIService()

    // TODO: Update this to your backend URL
    private let baseURL = "http://localhost:8000/api"

    private init() {}

    // MARK: - Authentication

    func login(request: LoginRequest) async throws -> AuthResponse {
        let url = URL(string: "\(baseURL)/auth/login")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        if httpResponse.statusCode == 401 {
            throw APIError.unauthorized
        }

        if httpResponse.statusCode != 200 {
            let errorMessage = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw APIError.serverError(errorMessage)
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(AuthResponse.self, from: data)
    }

    func register(request: RegisterRequest) async throws -> AuthResponse {
        let url = URL(string: "\(baseURL)/auth/register")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        if httpResponse.statusCode != 201 && httpResponse.statusCode != 200 {
            let errorMessage = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw APIError.serverError(errorMessage)
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(AuthResponse.self, from: data)
    }

    // MARK: - User

    func getCurrentUser() async throws -> User {
        let url = URL(string: "\(baseURL)/users/me")!
        let data = try await authenticatedRequest(url: url, method: "GET")

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(User.self, from: data)
    }

    func updateProfile(profile: UserProfile) async throws -> UserProfile {
        let url = URL(string: "\(baseURL)/users/profile")!
        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
        let body = try encoder.encode(profile)

        let data = try await authenticatedRequest(url: url, method: "PUT", body: body)

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(UserProfile.self, from: data)
    }

    // MARK: - Jobs

    func getJobQueue(limit: Int = 20) async throws -> [JobQueue] {
        let url = URL(string: "\(baseURL)/jobs/queue?limit=\(limit)")!
        let data = try await authenticatedRequest(url: url, method: "GET")

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode([JobQueue].self, from: data)
    }

    func swipeJob(jobId: String, direction: SwipeDirection) async throws {
        let url = URL(string: "\(baseURL)/jobs/swipe")!
        let swipeAction = SwipeAction(jobId: jobId, action: direction, timestamp: Date())

        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        let body = try encoder.encode(swipeAction)

        _ = try await authenticatedRequest(url: url, method: "POST", body: body)
    }

    func undoSwipe() async throws -> JobQueue? {
        let url = URL(string: "\(baseURL)/jobs/undo")!
        let data = try await authenticatedRequest(url: url, method: "POST")

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try? decoder.decode(JobQueue.self, from: data)
    }

    // MARK: - Applications

    func getApplications(status: ApplicationStatus? = nil) async throws -> [Application] {
        var urlString = "\(baseURL)/applications"
        if let status = status {
            urlString += "?status=\(status.rawValue)"
        }

        let url = URL(string: urlString)!
        let data = try await authenticatedRequest(url: url, method: "GET")

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode([Application].self, from: data)
    }

    func updateApplicationStatus(applicationId: String, status: ApplicationStatus) async throws {
        let url = URL(string: "\(baseURL)/applications/\(applicationId)/status")!
        let body = try JSONEncoder().encode(["status": status.rawValue])

        _ = try await authenticatedRequest(url: url, method: "PUT", body: body)
    }

    func submitCustomResponses(applicationId: String, responses: [CustomResponse]) async throws {
        let url = URL(string: "\(baseURL)/applications/\(applicationId)/responses")!
        let body = try JSONEncoder().encode(responses)

        _ = try await authenticatedRequest(url: url, method: "POST", body: body)
    }

    // MARK: - Helper Methods

    private func authenticatedRequest(
        url: URL,
        method: String,
        body: Data? = nil
    ) async throws -> Data {
        guard let token = KeychainHelper.shared.getToken() else {
            throw APIError.unauthorized
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = body

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        if httpResponse.statusCode == 401 {
            throw APIError.unauthorized
        }

        if httpResponse.statusCode < 200 || httpResponse.statusCode >= 300 {
            let errorMessage = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw APIError.serverError(errorMessage)
        }

        return data
    }
}
