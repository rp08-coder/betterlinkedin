//
//  MultiSelectView.swift
//  JobMatcherApp
//
//  Multi-selection view for profile fields
//

import SwiftUI

struct MultiSelectView: View {
    let title: String
    @Binding var items: [String]
    let availableItems: [String]
    let isEditing: Bool
    var allowCustom: Bool = false

    @State private var showingAddSheet = false
    @State private var customItem = ""

    var body: some View {
        List {
            if !items.isEmpty {
                Section("Selected") {
                    ForEach(items, id: \.self) { item in
                        HStack {
                            Text(item)
                            Spacer()
                            if isEditing {
                                Button(action: {
                                    items.removeAll { $0 == item }
                                }) {
                                    Image(systemName: "minus.circle.fill")
                                        .foregroundColor(.red)
                                }
                            } else {
                                Image(systemName: "checkmark")
                                    .foregroundColor(.blue)
                            }
                        }
                    }
                }
            }

            if isEditing {
                Section("Available") {
                    ForEach(availableItems.filter { !items.contains($0) }, id: \.self) { item in
                        Button(action: {
                            items.append(item)
                        }) {
                            HStack {
                                Text(item)
                                    .foregroundColor(.primary)
                                Spacer()
                                Image(systemName: "plus.circle.fill")
                                    .foregroundColor(.green)
                            }
                        }
                    }
                }

                if allowCustom {
                    Section {
                        Button(action: {
                            showingAddSheet = true
                        }) {
                            HStack {
                                Image(systemName: "plus.circle.fill")
                                Text("Add Custom")
                            }
                        }
                    }
                }
            } else if items.isEmpty {
                Section {
                    Text("No \(title.lowercased()) selected")
                        .foregroundColor(.secondary)
                }
            }
        }
        .navigationTitle(title)
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showingAddSheet) {
            NavigationView {
                Form {
                    TextField("Enter custom \(title.lowercased())", text: $customItem)
                }
                .navigationTitle("Add Custom")
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .navigationBarLeading) {
                        Button("Cancel") {
                            customItem = ""
                            showingAddSheet = false
                        }
                    }

                    ToolbarItem(placement: .navigationBarTrailing) {
                        Button("Add") {
                            if !customItem.isEmpty && !items.contains(customItem) {
                                items.append(customItem)
                            }
                            customItem = ""
                            showingAddSheet = false
                        }
                        .disabled(customItem.isEmpty)
                    }
                }
            }
        }
    }
}

#Preview {
    NavigationView {
        MultiSelectView(
            title: "Skills",
            items: .constant(["Swift", "Python", "JavaScript"]),
            availableItems: [
                "Swift", "Python", "JavaScript", "React", "Node.js",
                "AWS", "Docker", "Kubernetes"
            ],
            isEditing: true,
            allowCustom: true
        )
    }
}
