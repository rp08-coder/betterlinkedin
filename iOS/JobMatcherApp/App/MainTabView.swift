//
//  MainTabView.swift
//  JobMatcherApp
//
//  Main tab navigation container
//

import SwiftUI

struct MainTabView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @State private var selectedTab = 0
    @StateObject private var swipeViewModel = SwipeViewModel()
    @StateObject private var pipelineViewModel = PipelineViewModel()
    @StateObject private var profileViewModel = ProfileViewModel()

    var body: some View {
        TabView(selection: $selectedTab) {
            // Swipe Tab
            SwipeView()
                .environmentObject(swipeViewModel)
                .tabItem {
                    Label("Swipe", systemImage: "square.stack.3d.up.fill")
                }
                .tag(0)

            // Pipeline Tab
            PipelineView()
                .environmentObject(pipelineViewModel)
                .tabItem {
                    Label("Pipeline", systemImage: "briefcase.fill")
                }
                .badge(pipelineViewModel.outstandingCount)
                .tag(1)

            // Profile Tab
            ProfileView()
                .environmentObject(profileViewModel)
                .environmentObject(authViewModel)
                .tabItem {
                    Label("Profile", systemImage: "person.fill")
                }
                .tag(2)
        }
        .accentColor(.blue)
        .onAppear {
            Task {
                await loadInitialData()
            }
        }
    }

    private func loadInitialData() async {
        async let jobs = swipeViewModel.loadJobs()
        async let applications = pipelineViewModel.loadApplications()
        async let profile = profileViewModel.loadProfile()

        _ = await (jobs, applications, profile)
    }
}

#Preview {
    MainTabView()
        .environmentObject(AuthViewModel())
}
