//
//  AuthViewModel.swift
//  JobMatcherApp
//
//  Authentication view model
//

import Foundation
import SwiftUI

@MainActor
class AuthViewModel: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let apiService = APIService.shared

    init() {
        // Check if user is already logged in (token exists)
        if let token = KeychainHelper.shared.getToken() {
            self.isAuthenticated = true
            Task {
                await loadCurrentUser()
            }
        }
    }

    func login(email: String, password: String) async {
        isLoading = true
        errorMessage = nil

        do {
            let request = LoginRequest(email: email, password: password)
            let response = try await apiService.login(request: request)

            KeychainHelper.shared.saveToken(response.accessToken)
            self.currentUser = response.user
            self.isAuthenticated = true
        } catch {
            self.errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func register(email: String, password: String, firstName: String, lastName: String) async {
        isLoading = true
        errorMessage = nil

        do {
            let request = RegisterRequest(
                email: email,
                password: password,
                firstName: firstName,
                lastName: lastName
            )
            let response = try await apiService.register(request: request)

            KeychainHelper.shared.saveToken(response.accessToken)
            self.currentUser = response.user
            self.isAuthenticated = true
        } catch {
            self.errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func logout() {
        KeychainHelper.shared.deleteToken()
        self.currentUser = nil
        self.isAuthenticated = false
    }

    func loadCurrentUser() async {
        do {
            self.currentUser = try await apiService.getCurrentUser()
        } catch {
            // If loading user fails, log out
            logout()
        }
    }
}
