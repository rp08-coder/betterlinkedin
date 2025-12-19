//
//  JobCardView.swift
//  JobMatcherApp
//
//  Swipeable job card component
//

import SwiftUI

struct JobCardView: View {
    let job: Job
    @EnvironmentObject var viewModel: SwipeViewModel

    @State private var offset: CGSize = .zero
    @State private var isShowingDetails = false

    var body: some View {
        ZStack {
            // Card background
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.white)
                .shadow(radius: 8)

            VStack(alignment: .leading, spacing: 0) {
                // Company header
                HStack(spacing: 12) {
                    // Company logo placeholder
                    if let logoUrl = job.companyLogoUrl {
                        AsyncImage(url: URL(string: logoUrl)) { image in
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                        } placeholder: {
                            CompanyLogoPlaceholder(companyName: job.companyName)
                        }
                        .frame(width: 50, height: 50)
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                    } else {
                        CompanyLogoPlaceholder(companyName: job.companyName)
                    }

                    VStack(alignment: .leading, spacing: 4) {
                        Text(job.companyName)
                            .font(.headline)
                            .fontWeight(.bold)

                        Text(job.location)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }

                    Spacer()

                    // Relevance score
                    if let score = job.relevanceScore {
                        Text("\(score)%")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 5)
                            .background(scoreColor(for: score))
                            .cornerRadius(12)
                    }
                }
                .padding()

                Divider()

                ScrollView {
                    VStack(alignment: .leading, spacing: 16) {
                        // Job title
                        Text(job.jobTitle)
                            .font(.title2)
                            .fontWeight(.bold)

                        // Tags
                        HStack(spacing: 8) {
                            TagView(text: job.jobCategory, color: .blue)
                            TagView(text: job.sector, color: .purple)
                        }

                        // Description
                        VStack(alignment: .leading, spacing: 8) {
                            Text("About the Role")
                                .font(.headline)

                            Text(isShowingDetails ? job.description : job.shortDescription)
                                .font(.body)
                                .foregroundColor(.secondary)
                                .lineLimit(isShowingDetails ? nil : 3)

                            if !isShowingDetails && job.description.count > 200 {
                                Button("Read more") {
                                    withAnimation {
                                        isShowingDetails = true
                                    }
                                }
                                .font(.subheadline)
                                .foregroundColor(.blue)
                            }
                        }

                        // Requirements
                        if !job.requirementsList.isEmpty {
                            VStack(alignment: .leading, spacing: 8) {
                                Text("Requirements")
                                    .font(.headline)

                                ForEach(job.requirementsList, id: \.self) { requirement in
                                    HStack(alignment: .top, spacing: 8) {
                                        Image(systemName: "checkmark.circle.fill")
                                            .foregroundColor(.green)
                                            .font(.caption)

                                        Text(requirement)
                                            .font(.subheadline)
                                            .foregroundColor(.secondary)
                                    }
                                }
                            }
                        }

                        // Application platform
                        HStack {
                            Image(systemName: "link.circle.fill")
                                .foregroundColor(.blue)
                            Text("Apply via \(job.applicationPlatform.capitalized)")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding()
                }
            }

            // Swipe indicators
            if offset.width > 20 {
                VStack {
                    HStack {
                        Spacer()
                        Text("APPLY")
                            .font(.title)
                            .fontWeight(.bold)
                            .foregroundColor(.green)
                            .padding()
                            .overlay(
                                RoundedRectangle(cornerRadius: 10)
                                    .stroke(Color.green, lineWidth: 4)
                            )
                            .rotationEffect(.degrees(-15))
                            .padding()
                    }
                    Spacer()
                }
                .opacity(Double(offset.width / 100))
            } else if offset.width < -20 {
                VStack {
                    HStack {
                        Text("REJECT")
                            .font(.title)
                            .fontWeight(.bold)
                            .foregroundColor(.red)
                            .padding()
                            .overlay(
                                RoundedRectangle(cornerRadius: 10)
                                    .stroke(Color.red, lineWidth: 4)
                            )
                            .rotationEffect(.degrees(15))
                            .padding()
                        Spacer()
                    }
                    Spacer()
                }
                .opacity(Double(-offset.width / 100))
            }
        }
        .offset(offset)
        .rotationEffect(.degrees(Double(offset.width / 20)))
        .gesture(
            DragGesture()
                .onChanged { gesture in
                    offset = gesture.translation
                }
                .onEnded { gesture in
                    if abs(gesture.translation.width) > 150 {
                        // Swipe threshold reached
                        if gesture.translation.width > 0 {
                            // Swipe right - Apply
                            withAnimation {
                                offset = CGSize(width: 500, height: 0)
                            }
                            Task {
                                await viewModel.swipeRight()
                            }
                        } else {
                            // Swipe left - Reject
                            withAnimation {
                                offset = CGSize(width: -500, height: 0)
                            }
                            Task {
                                await viewModel.swipeLeft()
                            }
                        }
                    } else {
                        // Return to center
                        withAnimation(.spring()) {
                            offset = .zero
                        }
                    }
                }
        )
    }

    private func scoreColor(for score: Int) -> Color {
        if score >= 80 {
            return .green
        } else if score >= 60 {
            return .orange
        } else {
            return .gray
        }
    }
}

struct CompanyLogoPlaceholder: View {
    let companyName: String

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 8)
                .fill(LinearGradient(
                    colors: [.blue, .purple],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                ))

            Text(String(companyName.prefix(1)))
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.white)
        }
        .frame(width: 50, height: 50)
    }
}

struct TagView: View {
    let text: String
    let color: Color

    var body: some View {
        Text(text)
            .font(.caption)
            .fontWeight(.medium)
            .foregroundColor(color)
            .padding(.horizontal, 10)
            .padding(.vertical, 5)
            .background(color.opacity(0.1))
            .cornerRadius(8)
    }
}

#Preview {
    let sampleJob = Job(
        id: "1",
        sourceUrl: "https://example.com",
        companyName: "Acme Corp",
        companyLogoUrl: nil,
        jobTitle: "Senior Software Engineer",
        description: "We're looking for an experienced software engineer to join our team and help build the future of technology. This is a great opportunity to work with cutting-edge technologies and make a real impact.",
        requirements: "5+ years of experience\nProficiency in Swift and iOS development\nStrong problem-solving skills",
        jobCategory: "Engineering",
        sector: "Technology",
        location: "San Francisco, CA",
        datePosted: Date(),
        isActive: true,
        applicationUrl: "https://example.com/apply",
        applicationPlatform: "greenhouse",
        customQuestions: nil,
        relevanceScore: 85
    )

    return JobCardView(job: sampleJob)
        .environmentObject(SwipeViewModel())
        .padding()
}
