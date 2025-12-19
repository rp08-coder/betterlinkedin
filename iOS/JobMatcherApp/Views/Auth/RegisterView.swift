//
//  RegisterView.swift
//  JobMatcherApp
//
//  Registration view
//

import SwiftUI

struct RegisterView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @Binding var isShowingRegister: Bool

    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var firstName = ""
    @State private var lastName = ""
    @State private var passwordMismatch = false

    var body: some View {
        ScrollView {
            VStack(spacing: 30) {
                Spacer()
                    .frame(height: 20)

                // Logo/Title
                VStack(spacing: 10) {
                    Image(systemName: "briefcase.fill")
                        .font(.system(size: 50))
                        .foregroundColor(.white)

                    Text("Create Account")
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                }

                // Registration form
                VStack(spacing: 20) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("First Name")
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.9))

                        TextField("", text: $firstName)
                            .textFieldStyle(RoundedTextFieldStyle())
                            .autocorrectionDisabled()
                    }

                    VStack(alignment: .leading, spacing: 8) {
                        Text("Last Name")
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.9))

                        TextField("", text: $lastName)
                            .textFieldStyle(RoundedTextFieldStyle())
                            .autocorrectionDisabled()
                    }

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

                    VStack(alignment: .leading, spacing: 8) {
                        Text("Confirm Password")
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.9))

                        SecureField("", text: $confirmPassword)
                            .textFieldStyle(RoundedTextFieldStyle())
                            .onChange(of: confirmPassword) { _, newValue in
                                passwordMismatch = !newValue.isEmpty && newValue != password
                            }
                    }

                    if passwordMismatch {
                        Text("Passwords do not match")
                            .font(.caption)
                            .foregroundColor(.red)
                    }

                    if let errorMessage = authViewModel.errorMessage {
                        Text(errorMessage)
                            .font(.caption)
                            .foregroundColor(.red)
                            .padding(.horizontal)
                    }

                    Button(action: {
                        Task {
                            await authViewModel.register(
                                email: email,
                                password: password,
                                firstName: firstName,
                                lastName: lastName
                            )
                        }
                    }) {
                        if authViewModel.isLoading {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                .frame(maxWidth: .infinity)
                                .frame(height: 50)
                        } else {
                            Text("Sign Up")
                                .fontWeight(.semibold)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .frame(height: 50)
                        }
                    }
                    .background(Color.blue)
                    .cornerRadius(12)
                    .disabled(
                        authViewModel.isLoading ||
                        email.isEmpty ||
                        password.isEmpty ||
                        confirmPassword.isEmpty ||
                        firstName.isEmpty ||
                        lastName.isEmpty ||
                        passwordMismatch
                    )
                    .opacity(isFormValid ? 1.0 : 0.6)
                }
                .padding(.horizontal, 30)

                // Login link
                HStack {
                    Text("Already have an account?")
                        .foregroundColor(.white.opacity(0.9))

                    Button("Log In") {
                        isShowingRegister = false
                    }
                    .foregroundColor(.white)
                    .fontWeight(.semibold)
                }
                .font(.subheadline)

                Spacer()
                    .frame(height: 30)
            }
        }
    }

    private var isFormValid: Bool {
        !email.isEmpty &&
        !password.isEmpty &&
        !confirmPassword.isEmpty &&
        !firstName.isEmpty &&
        !lastName.isEmpty &&
        !passwordMismatch &&
        !authViewModel.isLoading
    }
}

#Preview {
    RegisterView(isShowingRegister: .constant(true))
        .environmentObject(AuthViewModel())
        .background(
            LinearGradient(
                colors: [Color.blue.opacity(0.6), Color.purple.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
}
