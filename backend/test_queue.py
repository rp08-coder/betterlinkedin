#!/usr/bin/env python3
import requests
import json

# Login
print("🔐 Logging in...")
login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": "user@founded.com", "password": "password123"}
)
print(f"Login status: {login_response.status_code}")
login_data = login_response.json()
token = login_data["access_token"]
print(f"Token: {token[:50]}...")
print()

# Get queue
print("📋 Fetching queue...")
queue_response = requests.get(
    "http://localhost:8000/api/jobs/queue",
    headers={"Authorization": f"Bearer {token}"}
)
print(f"Queue status: {queue_response.status_code}")
print(f"Response: {queue_response.text[:500]}")
print()

if queue_response.status_code == 200:
    jobs = queue_response.json()
    print(f"✅ Found {len(jobs)} jobs in queue!")
    for i, job in enumerate(jobs[:5], 1):
        print(f"{i}. {job['job']['job_title']} at {job['job']['company_name']} ({job['relevance_score']*100}% match)")
else:
    print(f"❌ Error: {queue_response.json()}")
