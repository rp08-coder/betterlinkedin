//
//  ProfileView.swift
//  JobMatcherApp
//
//  User profile and settings view
//

import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var profileViewModel: ProfileViewModel
    @EnvironmentObject var authViewModel: AuthViewModel

    @State private var isEditing = false
    @State private var showingLogoutAlert = false

    var body: some View {
        NavigationView {
            Form {
                // Basic Information
                Section("Basic Information") {
                    HStack {
                        Text("First Name")
                        Spacer()
                        if isEditing {
                            TextField("First Name", text: $profileViewModel.profile.firstName)
                                .multilineTextAlignment(.trailing)
                        } else {
                            Text(profileViewModel.profile.firstName)
                                .foregroundColor(.secondary)
                        }
                    }

                    HStack {
                        Text("Last Name")
                        Spacer()
                        if isEditing {
                            TextField("Last Name", text: $profileViewModel.profile.lastName)
                                .multilineTextAlignment(.trailing)
                        } else {
                            Text(profileViewModel.profile.lastName)
                                .foregroundColor(.secondary)
                        }
                    }

                    HStack {
                        Text("Email")
                        Spacer()
                        Text(authViewModel.currentUser?.email ?? "")
                            .foregroundColor(.secondary)
                    }

                    HStack {
                        Text("City")
                        Spacer()
                        if isEditing {
                            TextField("City", text: $profileViewModel.profile.city)
                                .multilineTextAlignment(.trailing)
                        } else {
                            Text(profileViewModel.profile.city)
                                .foregroundColor(.secondary)
                        }
                    }

                    HStack {
                        Text("Phone")
                        Spacer()
                        if isEditing {
                            TextField("Phone (optional)", text: Binding(
                                get: { profileViewModel.profile.phone ?? "" },
                                set: { profileViewModel.profile.phone = $0.isEmpty ? nil : $0 }
                            ))
                            .multilineTextAlignment(.trailing)
                            .keyboardType(.phonePad)
                        } else {
                            Text(profileViewModel.profile.phone ?? "Not provided")
                                .foregroundColor(.secondary)
                        }
                    }
                }

                // Experience
                Section("Experience") {
                    HStack {
                        Text("Years of Experience")
                        Spacer()
                        if isEditing {
                            TextField("Years", value: $profileViewModel.profile.yearsExperience, format: .number)
                                .multilineTextAlignment(.trailing)
                                .keyboardType(.numberPad)
                                .frame(width: 60)
                        } else {
                            Text("\(profileViewModel.profile.yearsExperience)")
                                .foregroundColor(.secondary)
                        }
                    }

                    NavigationLink("Sectors") {
                        MultiSelectView(
                            title: "Sectors",
                            items: $profileViewModel.profile.sectors,
                            availableItems: [
                                "Fintech", "Healthcare", "AI/ML", "E-commerce",
                                "SaaS", "Consumer", "Enterprise", "Cybersecurity",
                                "EdTech", "Climate Tech", "Biotech", "Crypto/Web3"
                            ],
                            isEditing: isEditing
                        )
                    }

                    NavigationLink("Job Types") {
                        MultiSelectView(
                            title: "Job Types",
                            items: $profileViewModel.profile.jobTypes,
                            availableItems: [
                                "Software Engineer", "Product Manager", "Designer",
                                "Data Scientist", "Business Operations", "Sales",
                                "Marketing", "Customer Success", "DevOps Engineer",
                                "QA Engineer", "Security Engineer", "Engineering Manager"
                            ],
                            isEditing: isEditing
                        )
                    }

                    NavigationLink("Skills") {
                        MultiSelectView(
                            title: "Skills",
                            items: $profileViewModel.profile.skills,
                            availableItems: [
                                "Swift", "Python", "JavaScript", "React", "Node.js",
                                "AWS", "Docker", "Kubernetes", "SQL", "MongoDB",
                                "Machine Learning", "iOS Development", "Android",
                                "TypeScript", "Go", "Rust"
                            ],
                            isEditing: isEditing,
                            allowCustom: true
                        )
                    }
                }

                // Preferences
                Section("Preferences") {
                    HStack {
                        Text("Salary Minimum")
                        Spacer()
                        if isEditing {
                            TextField("Optional", value: $profileViewModel.profile.salaryMin, format: .currency(code: "USD"))
                                .multilineTextAlignment(.trailing)
                                .keyboardType(.numberPad)
                        } else {
                            if let salary = profileViewModel.profile.salaryMin {
                                Text(salary, format: .currency(code: "USD"))
                                    .foregroundColor(.secondary)
                            } else {
                                Text("Not specified")
                                    .foregroundColor(.secondary)
                            }
                        }
                    }

                    HStack {
                        Text("Daily Application Limit")
                        Spacer()
                        if isEditing {
                            Stepper("\(profileViewModel.profile.dailyApplicationLimit)", value: $profileViewModel.profile.dailyApplicationLimit, in: 1...50)
                        } else {
                            Text("\(profileViewModel.profile.dailyApplicationLimit)")
                                .foregroundColor(.secondary)
                        }
                    }
                }

                // Notifications
                Section("Notifications") {
                    Toggle("New Jobs", isOn: $profileViewModel.profile.notificationPreferences.enableNewJobs)
                        .disabled(!isEditing)

                    Toggle("Application Updates", isOn: $profileViewModel.profile.notificationPreferences.enableApplicationUpdates)
                        .disabled(!isEditing)

                    Toggle("Weekly Summary", isOn: $profileViewModel.profile.notificationPreferences.enableWeeklySummary)
                        .disabled(!isEditing)

                    if isEditing {
                        HStack {
                            Text("Quiet Hours")
                            Spacer()
                            Text("\(profileViewModel.profile.notificationPreferences.quietHoursStart):00 - \(profileViewModel.profile.notificationPreferences.quietHoursEnd):00")
                                .foregroundColor(.secondary)
                        }
                    }
                }

                // Resume
                Section("Resume") {
                    if let resumeUrl = profileViewModel.profile.resumeUrl {
                        Link(destination: URL(string: resumeUrl)!) {
                            HStack {
                                Image(systemName: "doc.fill")
                                Text("View Resume")
                                Spacer()
                                Image(systemName: "arrow.up.right")
                            }
                        }
                    } else {
                        Text("No resume uploaded")
                            .foregroundColor(.secondary)
                    }

                    if isEditing {
                        Button("Upload Resume") {
                            // TODO: Implement file picker
                        }
                    }
                }

                // Account
                Section("Account") {
                    Button("Log Out") {
                        showingLogoutAlert = true
                    }
                    .foregroundColor(.red)
                }
            }
            .navigationTitle("Profile")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(isEditing ? "Save" : "Edit") {
                        if isEditing {
                            Task {
                                await profileViewModel.saveProfile()
                            }
                        }
                        isEditing.toggle()
                    }
                    .disabled(profileViewModel.isSaving)
                }
            }
            .alert("Success", isPresented: .constant(profileViewModel.successMessage != nil)) {
                Button("OK") {
                    profileViewModel.successMessage = nil
                }
            } message: {
                if let message = profileViewModel.successMessage {
                    Text(message)
                }
            }
            .alert("Error", isPresented: .constant(profileViewModel.errorMessage != nil)) {
                Button("OK") {
                    profileViewModel.errorMessage = nil
                }
            } message: {
                if let error = profileViewModel.errorMessage {
                    Text(error)
                }
            }
            .alert("Log Out", isPresented: $showingLogoutAlert) {
                Button("Cancel", role: .cancel) {}
                Button("Log Out", role: .destructive) {
                    authViewModel.logout()
                }
            } message: {
                Text("Are you sure you want to log out?")
            }
        }
    }
}

#Preview {
    ProfileView()
        .environmentObject(ProfileViewModel())
        .environmentObject(AuthViewModel())
}
