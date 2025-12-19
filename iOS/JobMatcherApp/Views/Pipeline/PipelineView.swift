//
//  PipelineView.swift
//  JobMatcherApp
//
//  Application pipeline view with status tabs
//

import SwiftUI

struct PipelineView: View {
    @EnvironmentObject var viewModel: PipelineViewModel
    @State private var selectedStatus: ApplicationStatus = .outstanding

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Status tabs
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 12) {
                        ForEach(ApplicationStatus.allCases, id: \.self) { status in
                            StatusTabButton(
                                status: status,
                                count: viewModel.applicationsByStatus[status]?.count ?? 0,
                                isSelected: selectedStatus == status,
                                action: {
                                    selectedStatus = status
                                }
                            )
                        }
                    }
                    .padding(.horizontal)
                    .padding(.vertical, 12)
                }
                .background(Color(.systemGroupedBackground))

                Divider()

                // Application list
                if viewModel.isLoading {
                    Spacer()
                    ProgressView("Loading applications...")
                    Spacer()
                } else {
                    let applications = viewModel.applicationsByStatus[selectedStatus] ?? []

                    if applications.isEmpty {
                        EmptyStateView(status: selectedStatus)
                    } else {
                        ScrollView {
                            LazyVStack(spacing: 12) {
                                ForEach(applications) { application in
                                    NavigationLink(destination: ApplicationDetailView(application: application)) {
                                        ApplicationCardView(application: application)
                                    }
                                    .buttonStyle(PlainButtonStyle())
                                }
                            }
                            .padding()
                        }
                    }
                }
            }
            .navigationTitle("Pipeline")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        Task {
                            await viewModel.refreshApplications()
                        }
                    }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
        }
        .alert("Error", isPresented: .constant(viewModel.errorMessage != nil)) {
            Button("OK") {
                viewModel.errorMessage = nil
            }
        } message: {
            if let error = viewModel.errorMessage {
                Text(error)
            }
        }
    }
}

struct StatusTabButton: View {
    let status: ApplicationStatus
    let count: Int
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                HStack(spacing: 4) {
                    Image(systemName: status.icon)
                        .font(.caption)

                    Text(status.displayName)
                        .font(.subheadline)
                        .fontWeight(isSelected ? .semibold : .regular)

                    if count > 0 {
                        Text("(\(count))")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .foregroundColor(isSelected ? .blue : .secondary)

                if isSelected {
                    Rectangle()
                        .fill(Color.blue)
                        .frame(height: 2)
                } else {
                    Rectangle()
                        .fill(Color.clear)
                        .frame(height: 2)
                }
            }
        }
    }
}

struct ApplicationCardView: View {
    let application: Application

    var body: some View {
        HStack(spacing: 12) {
            // Company logo or placeholder
            if let logoUrl = application.job.companyLogoUrl {
                AsyncImage(url: URL(string: logoUrl)) { image in
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                } placeholder: {
                    CompanyLogoPlaceholder(companyName: application.job.companyName)
                }
                .frame(width: 50, height: 50)
                .clipShape(RoundedRectangle(cornerRadius: 8))
            } else {
                CompanyLogoPlaceholder(companyName: application.job.companyName)
            }

            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(application.job.jobTitle)
                        .font(.headline)
                        .foregroundColor(.primary)

                    if application.isExpired {
                        Text("(Expired)")
                            .font(.caption)
                            .foregroundColor(.red)
                    }
                }

                Text(application.job.companyName)
                    .font(.subheadline)
                    .foregroundColor(.secondary)

                if let dateApplied = application.dateApplied {
                    Text("Applied \(dateApplied, style: .relative) ago")
                        .font(.caption)
                        .foregroundColor(.secondary)
                } else {
                    Text("Swiped \(application.dateSwiped, style: .relative) ago")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            Spacer()

            Image(systemName: "chevron.right")
                .foregroundColor(.secondary)
                .font(.caption)
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.05), radius: 4)
    }
}

struct EmptyStateView: View {
    let status: ApplicationStatus

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: status.icon)
                .font(.system(size: 50))
                .foregroundColor(.secondary)

            Text("No \(status.displayName)")
                .font(.headline)

            Text(emptyMessage(for: status))
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private func emptyMessage(for status: ApplicationStatus) -> String {
        switch status {
        case .outstanding:
            return "All applications are complete. Keep swiping to find more jobs!"
        case .applied:
            return "You haven't applied to any jobs yet. Start swiping!"
        case .interviewing:
            return "No active interviews. Move applications here when you get interview requests."
        case .offered:
            return "No offers yet. Keep applying and interviewing!"
        case .rejected:
            return "No rejections. That's great!"
        }
    }
}

#Preview {
    PipelineView()
        .environmentObject(PipelineViewModel())
}
