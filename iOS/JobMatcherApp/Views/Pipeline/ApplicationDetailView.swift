//
//  ApplicationDetailView.swift
//  JobMatcherApp
//
//  Detailed view for a single application
//

import SwiftUI

struct ApplicationDetailView: View {
    let application: Application
    @EnvironmentObject var viewModel: PipelineViewModel
    @Environment(\.dismiss) var dismiss

    @State private var selectedStatus: ApplicationStatus
    @State private var showingStatusPicker = false

    init(application: Application) {
        self.application = application
        _selectedStatus = State(initialValue: application.status)
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                // Company header
                HStack(spacing: 16) {
                    if let logoUrl = application.job.companyLogoUrl {
                        AsyncImage(url: URL(string: logoUrl)) { image in
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                        } placeholder: {
                            CompanyLogoPlaceholder(companyName: application.job.companyName)
                        }
                        .frame(width: 80, height: 80)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                    } else {
                        CompanyLogoPlaceholder(companyName: application.job.companyName)
                            .frame(width: 80, height: 80)
                    }

                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text(application.job.companyName)
                                .font(.title2)
                                .fontWeight(.bold)

                            if application.isExpired {
                                Text("(Expired)")
                                    .font(.caption)
                                    .foregroundColor(.white)
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 4)
                                    .background(Color.red)
                                    .cornerRadius(8)
                            }
                        }

                        Text(application.job.jobTitle)
                            .font(.headline)
                            .foregroundColor(.secondary)

                        Text(application.job.location)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
                .padding()
                .background(Color(.systemBackground))
                .cornerRadius(12)
                .shadow(color: Color.black.opacity(0.05), radius: 4)

                // Status section
                VStack(alignment: .leading, spacing: 12) {
                    Text("Status")
                        .font(.headline)

                    Button(action: {
                        showingStatusPicker = true
                    }) {
                        HStack {
                            Image(systemName: selectedStatus.icon)
                            Text(selectedStatus.displayName)
                            Spacer()
                            Image(systemName: "chevron.down")
                        }
                        .padding()
                        .background(Color(.secondarySystemBackground))
                        .cornerRadius(10)
                    }
                    .foregroundColor(.primary)
                }
                .padding(.horizontal)

                // Timeline
                VStack(alignment: .leading, spacing: 12) {
                    Text("Timeline")
                        .font(.headline)
                        .padding(.horizontal)

                    VStack(alignment: .leading, spacing: 16) {
                        TimelineItem(
                            icon: "hand.point.up.left.fill",
                            title: "Swiped Right",
                            date: application.dateSwiped
                        )

                        if let dateApplied = application.dateApplied {
                            TimelineItem(
                                icon: "paperplane.fill",
                                title: "Application Submitted",
                                date: dateApplied
                            )
                        }
                    }
                    .padding()
                    .background(Color(.systemBackground))
                    .cornerRadius(12)
                    .shadow(color: Color.black.opacity(0.05), radius: 4)
                    .padding(.horizontal)
                }

                // Job details
                VStack(alignment: .leading, spacing: 12) {
                    Text("Job Description")
                        .font(.headline)

                    Text(application.job.description)
                        .font(.body)
                        .foregroundColor(.secondary)

                    if !application.job.requirements.isEmpty {
                        Text("Requirements")
                            .font(.headline)
                            .padding(.top, 8)

                        Text(application.job.requirements)
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                }
                .padding()
                .background(Color(.systemBackground))
                .cornerRadius(12)
                .shadow(color: Color.black.opacity(0.05), radius: 4)
                .padding(.horizontal)

                // Application link
                if let url = URL(string: application.job.applicationUrl) {
                    Link(destination: url) {
                        HStack {
                            Image(systemName: "link.circle.fill")
                            Text("View Original Posting")
                            Spacer()
                            Image(systemName: "arrow.up.right")
                        }
                        .padding()
                        .background(Color.blue.opacity(0.1))
                        .foregroundColor(.blue)
                        .cornerRadius(10)
                    }
                    .padding(.horizontal)
                }
            }
            .padding(.vertical)
        }
        .background(Color(.systemGroupedBackground))
        .navigationBarTitleDisplayMode(.inline)
        .confirmationDialog("Update Status", isPresented: $showingStatusPicker) {
            ForEach(ApplicationStatus.allCases, id: \.self) { status in
                Button(status.displayName) {
                    selectedStatus = status
                    Task {
                        await viewModel.updateStatus(for: application, to: status)
                    }
                }
            }

            Button("Cancel", role: .cancel) {}
        }
    }
}

struct TimelineItem: View {
    let icon: String
    let title: String
    let date: Date

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(.blue)
                .frame(width: 24)

            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)

                Text(date.formatted(date: .abbreviated, time: .shortened))
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Spacer()
        }
    }
}

#Preview {
    let sampleApplication = Application(
        id: "1",
        userId: "user1",
        job: Job(
            id: "1",
            sourceUrl: "https://example.com",
            companyName: "Acme Corp",
            companyLogoUrl: nil,
            jobTitle: "Senior Software Engineer",
            description: "We're looking for an experienced software engineer to join our team.",
            requirements: "5+ years of experience in iOS development",
            jobCategory: "Engineering",
            sector: "Technology",
            location: "San Francisco, CA",
            datePosted: Date(),
            isActive: true,
            applicationUrl: "https://example.com/apply",
            applicationPlatform: "greenhouse",
            customQuestions: nil,
            relevanceScore: 85
        ),
        status: .applied,
        dateSwiped: Date().addingTimeInterval(-86400 * 2),
        dateApplied: Date().addingTimeInterval(-86400),
        customResponses: nil,
        coverLetter: nil,
        notes: nil,
        interviewStage: nil,
        offerDetails: nil
    )

    return NavigationView {
        ApplicationDetailView(application: sampleApplication)
            .environmentObject(PipelineViewModel())
    }
}
