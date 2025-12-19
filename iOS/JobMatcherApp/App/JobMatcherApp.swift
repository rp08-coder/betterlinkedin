//
//  JobMatcherApp.swift
//  JobMatcherApp
//
//  Main app entry point
//

import SwiftUI

@main
struct JobMatcherApp: App {
    @StateObject private var authViewModel = AuthViewModel()

    var body: some Scene {
        WindowGroup {
            if authViewModel.isAuthenticated {
                MainTabView()
                    .environmentObject(authViewModel)
            } else {
                AuthenticationView()
                    .environmentObject(authViewModel)
            }
        }
    }
}
