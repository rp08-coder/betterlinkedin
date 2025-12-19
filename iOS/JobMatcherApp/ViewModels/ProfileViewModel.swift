//
//  ProfileViewModel.swift
//  JobMatcherApp
//
//  View model for user profile
//

import Foundation
import SwiftUI

@MainActor
class ProfileViewModel: ObservableObject {
    @Published var profile: UserProfile
    @Published var isLoading = false
    @Published var isSaving = false
    @Published var errorMessage: String?
    @Published var successMessage: String?

    private let apiService = APIService.shared

    init() {
        // Initialize with empty profile
        self.profile = UserProfile()
    }

    func loadProfile() async {
        isLoading = true
        errorMessage = nil

        do {
            let user = try await apiService.getCurrentUser()
            if let userProfile = user.profile {
                self.profile = userProfile
            }
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func saveProfile() async {
        isSaving = true
        errorMessage = nil
        successMessage = nil

        do {
            let updatedProfile = try await apiService.updateProfile(profile: profile)
            self.profile = updatedProfile
            successMessage = "Profile saved successfully"

            // Clear success message after 3 seconds
            Task {
                try? await Task.sleep(nanoseconds: 3_000_000_000)
                successMessage = nil
            }
        } catch {
            errorMessage = error.localizedDescription
        }

        isSaving = false
    }

    func addSector(_ sector: String) {
        if !profile.sectors.contains(sector) {
            profile.sectors.append(sector)
        }
    }

    func removeSector(_ sector: String) {
        profile.sectors.removeAll { $0 == sector }
    }

    func addJobType(_ jobType: String) {
        if !profile.jobTypes.contains(jobType) {
            profile.jobTypes.append(jobType)
        }
    }

    func removeJobType(_ jobType: String) {
        profile.jobTypes.removeAll { $0 == jobType }
    }

    func addSkill(_ skill: String) {
        if !profile.skills.contains(skill) {
            profile.skills.append(skill)
        }
    }

    func removeSkill(_ skill: String) {
        profile.skills.removeAll { $0 == skill }
    }
}
