//
//  PipelineViewModel.swift
//  JobMatcherApp
//
//  View model for application pipeline
//

import Foundation
import SwiftUI

@MainActor
class PipelineViewModel: ObservableObject {
    @Published var applications: [Application] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var selectedStatus: ApplicationStatus = .outstanding

    private let apiService = APIService.shared

    var outstandingCount: Int {
        applications.filter { $0.status == .outstanding }.count
    }

    var applicationsByStatus: [ApplicationStatus: [Application]] {
        Dictionary(grouping: applications) { $0.status }
    }

    func loadApplications() async {
        isLoading = true
        errorMessage = nil

        do {
            applications = try await apiService.getApplications()
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func loadApplications(for status: ApplicationStatus) async {
        isLoading = true
        errorMessage = nil

        do {
            applications = try await apiService.getApplications(status: status)
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func updateStatus(for application: Application, to newStatus: ApplicationStatus) async {
        do {
            try await apiService.updateApplicationStatus(
                applicationId: application.id,
                status: newStatus
            )

            // Update local state
            if let index = applications.firstIndex(where: { $0.id == application.id }) {
                applications[index].status = newStatus
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func submitResponses(for application: Application, responses: [CustomResponse]) async {
        do {
            try await apiService.submitCustomResponses(
                applicationId: application.id,
                responses: responses
            )

            // Update local state
            if let index = applications.firstIndex(where: { $0.id == application.id }) {
                applications[index].customResponses = responses
                applications[index].status = .applied
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func refreshApplications() async {
        await loadApplications()
    }
}
