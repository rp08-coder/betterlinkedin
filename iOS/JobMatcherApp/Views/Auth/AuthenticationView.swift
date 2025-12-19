//
//  AuthenticationView.swift
//  JobMatcherApp
//
//  Main authentication view (login/register switcher)
//

import SwiftUI

struct AuthenticationView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @State private var isShowingRegister = false

    var body: some View {
        NavigationView {
            ZStack {
                // Background gradient
                LinearGradient(
                    colors: [Color.blue.opacity(0.6), Color.purple.opacity(0.6)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()

                VStack(spacing: 0) {
                    if isShowingRegister {
                        RegisterView(isShowingRegister: $isShowingRegister)
                    } else {
                        LoginView(isShowingRegister: $isShowingRegister)
                    }
                }
            }
        }
    }
}

#Preview {
    AuthenticationView()
        .environmentObject(AuthViewModel())
}
