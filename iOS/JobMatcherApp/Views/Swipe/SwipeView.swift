//
//  SwipeView.swift
//  JobMatcherApp
//
//  Main swipe interface view
//

import SwiftUI

struct SwipeView: View {
    @EnvironmentObject var viewModel: SwipeViewModel

    var body: some View {
        NavigationView {
            ZStack {
                // Background
                Color(.systemGroupedBackground)
                    .ignoresSafeArea()

                if viewModel.isLoading {
                    ProgressView("Loading jobs...")
                } else if !viewModel.hasMoreJobs {
                    NoMoreJobsView(onRefresh: {
                        Task {
                            await viewModel.refreshJobs()
                        }
                    })
                } else {
                    VStack(spacing: 0) {
                        // Header with job count
                        HStack {
                            Text("\(viewModel.remainingJobsCount) jobs remaining")
                                .font(.headline)
                                .foregroundColor(.secondary)

                            Spacer()

                            Button(action: {
                                Task {
                                    await viewModel.refreshJobs()
                                }
                            }) {
                                Image(systemName: "arrow.clockwise")
                                    .font(.title3)
                            }
                        }
                        .padding()

                        // Card stack
                        ZStack {
                            if let job = viewModel.currentJob {
                                JobCardView(job: job)
                                    .environmentObject(viewModel)
                            }
                        }
                        .padding(.horizontal)

                        // Action buttons
                        HStack(spacing: 40) {
                            // Reject button
                            Button(action: {
                                Task {
                                    await viewModel.swipeLeft()
                                }
                            }) {
                                Image(systemName: "xmark")
                                    .font(.system(size: 30))
                                    .foregroundColor(.white)
                                    .frame(width: 60, height: 60)
                                    .background(Color.red)
                                    .clipShape(Circle())
                                    .shadow(radius: 4)
                            }

                            // Apply button
                            Button(action: {
                                Task {
                                    await viewModel.swipeRight()
                                }
                            }) {
                                Image(systemName: "heart.fill")
                                    .font(.system(size: 30))
                                    .foregroundColor(.white)
                                    .frame(width: 60, height: 60)
                                    .background(Color.green)
                                    .clipShape(Circle())
                                    .shadow(radius: 4)
                            }
                        }
                        .padding(.vertical, 30)

                        // Undo button (shows for 5 seconds after swipe)
                        if viewModel.showUndoButton {
                            Button(action: {
                                Task {
                                    await viewModel.undo()
                                }
                            }) {
                                HStack {
                                    Image(systemName: "arrow.uturn.backward")
                                    Text("Undo")
                                        .fontWeight(.semibold)
                                }
                                .foregroundColor(.blue)
                                .padding(.horizontal, 20)
                                .padding(.vertical, 10)
                                .background(Color.blue.opacity(0.1))
                                .cornerRadius(20)
                            }
                            .transition(.move(edge: .bottom).combined(with: .opacity))
                        }

                        Spacer()
                            .frame(height: 20)
                    }
                }
            }
            .navigationTitle("Jobs")
            .navigationBarTitleDisplayMode(.inline)
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

struct NoMoreJobsView: View {
    let onRefresh: () -> Void

    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 60))
                .foregroundColor(.green)

            Text("All caught up!")
                .font(.title2)
                .fontWeight(.bold)

            Text("You've reviewed all available jobs.\nCheck back later for more matches.")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)

            Button(action: onRefresh) {
                HStack {
                    Image(systemName: "arrow.clockwise")
                    Text("Refresh")
                }
                .fontWeight(.semibold)
                .foregroundColor(.white)
                .padding(.horizontal, 30)
                .padding(.vertical, 15)
                .background(Color.blue)
                .cornerRadius(25)
            }
            .padding(.top, 20)
        }
    }
}

#Preview {
    SwipeView()
        .environmentObject(SwipeViewModel())
}
