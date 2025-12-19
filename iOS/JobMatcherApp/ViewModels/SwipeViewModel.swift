//
//  SwipeViewModel.swift
//  JobMatcherApp
//
//  View model for swipe functionality
//

import Foundation
import SwiftUI

@MainActor
class SwipeViewModel: ObservableObject {
    @Published var jobQueue: [JobQueue] = []
    @Published var currentJobIndex = 0
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var showUndoButton = false
    @Published var lastSwipedJob: JobQueue?
    @Published var lastSwipeDirection: SwipeDirection?

    private let apiService = APIService.shared
    private var undoTimer: Timer?

    var currentJob: Job? {
        guard currentJobIndex < jobQueue.count else { return nil }
        return jobQueue[currentJobIndex].job
    }

    var hasMoreJobs: Bool {
        currentJobIndex < jobQueue.count
    }

    var remainingJobsCount: Int {
        max(0, jobQueue.count - currentJobIndex)
    }

    func loadJobs() async {
        isLoading = true
        errorMessage = nil

        do {
            jobQueue = try await apiService.getJobQueue(limit: 50)
            currentJobIndex = 0
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func swipeLeft() async {
        guard let job = currentJob else { return }

        lastSwipedJob = jobQueue[currentJobIndex]
        lastSwipeDirection = .left
        currentJobIndex += 1

        do {
            try await apiService.swipeJob(jobId: job.id, direction: .left)
            showUndo()
        } catch {
            // Revert on error
            currentJobIndex -= 1
            errorMessage = error.localizedDescription
        }
    }

    func swipeRight() async {
        guard let job = currentJob else { return }

        lastSwipedJob = jobQueue[currentJobIndex]
        lastSwipeDirection = .right
        currentJobIndex += 1

        do {
            try await apiService.swipeJob(jobId: job.id, direction: .right)
            showUndo()
        } catch {
            // Revert on error
            currentJobIndex -= 1
            errorMessage = error.localizedDescription
        }
    }

    func undo() async {
        cancelUndoTimer()
        showUndoButton = false

        do {
            if let restoredJob = try await apiService.undoSwipe() {
                // Move back one position
                currentJobIndex = max(0, currentJobIndex - 1)
                // Update the job in the queue
                if currentJobIndex < jobQueue.count {
                    jobQueue[currentJobIndex] = restoredJob
                }
                lastSwipedJob = nil
                lastSwipeDirection = nil
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func refreshJobs() async {
        await loadJobs()
    }

    private func showUndo() {
        showUndoButton = true

        // Cancel any existing timer
        cancelUndoTimer()

        // Hide undo button after 5 seconds
        undoTimer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: false) { [weak self] _ in
            Task { @MainActor in
                self?.showUndoButton = false
                self?.lastSwipedJob = nil
                self?.lastSwipeDirection = nil
            }
        }
    }

    private func cancelUndoTimer() {
        undoTimer?.invalidate()
        undoTimer = nil
    }

    deinit {
        cancelUndoTimer()
    }
}
