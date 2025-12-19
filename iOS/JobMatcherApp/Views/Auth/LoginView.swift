//
//  LoginView.swift
//  JobMatcherApp
//
//  Login view
//

import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @Binding var isShowingRegister: Bool

    @State private var email = ""
    @State private var password = ""

    var body: some View {
        VStack(spacing: 30) {
            Spacer()

            // Logo/Title
            VStack(spacing: 10) {
                Image(systemName: "briefcase.fill")
                    .font(.system(size: 60))
                    .foregroundColor(.white)

                Text("JobMatcher")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.white)

                Text("Swipe. Match. Apply.")
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.9))
            }

            Spacer()

            // Login form
            VStack(spacing: 20) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Email")
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.9))

                    TextField("", text: $email)
                        .textFieldStyle(RoundedTextFieldStyle())
                        .textInputAutocapitalization(.never)
                        .keyboardType(.emailAddress)
                        .autocorrectionDisabled()
                }

                VStack(alignment: .leading, spacing: 8) {
                    Text("Password")
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.9))

                    SecureField("", text: $password)
                        .textFieldStyle(RoundedTextFieldStyle())
                }

                if let errorMessage = authViewModel.errorMessage {
                    Text(errorMessage)
                        .font(.caption)
                        .foregroundColor(.red)
                        .padding(.horizontal)
                }

                Button(action: {
                    Task {
                        await authViewModel.login(email: email, password: password)
                    }
                }) {
                    if authViewModel.isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                    } else {
                        Text("Log In")
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                    }
                }
                .background(Color.blue)
                .cornerRadius(12)
                .disabled(authViewModel.isLoading || email.isEmpty || password.isEmpty)
                .opacity((authViewModel.isLoading || email.isEmpty || password.isEmpty) ? 0.6 : 1.0)
            }
            .padding(.horizontal, 30)

            // Register link
            HStack {
                Text("Don't have an account?")
                    .foregroundColor(.white.opacity(0.9))

                Button("Sign Up") {
                    isShowingRegister = true
                }
                .foregroundColor(.white)
                .fontWeight(.semibold)
            }
            .font(.subheadline)

            Spacer()
        }
        .padding()
    }
}

// Custom text field style
struct RoundedTextFieldStyle: TextFieldStyle {
    func _body(configuration: TextField<Self._Label>) -> some View {
        configuration
            .padding()
            .background(Color.white.opacity(0.9))
            .cornerRadius(10)
    }
}

#Preview {
    LoginView(isShowingRegister: .constant(false))
        .environmentObject(AuthViewModel())
        .background(
            LinearGradient(
                colors: [Color.blue.opacity(0.6), Color.purple.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
}
