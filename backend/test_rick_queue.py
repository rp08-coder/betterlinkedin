#!/usr/bin/env python3
import requests
import json

# Login
print("🔐 Logging in as rickpradhan@gmail.com...")
login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": "rickpradhan@gmail.com", "password": "password123"}
)
login_data = login_response.json()
token = login_data["access_token"]
print(f"✅ Login successful!\n")

# Get queue
print("📋 Fetching your job queue...")
queue_response = requests.get(
    "http://localhost:8000/api/jobs/queue",
    headers={"Authorization": f"Bearer {token}"}
)

if queue_response.status_code == 200:
    jobs = queue_response.json()
    print(f"✅ Found {len(jobs)} jobs in your queue!\n")
    print("="*70)
    for i, item in enumerate(jobs, 1):
        job = item['job']
        score = item['relevance_score']
        print(f"{i}. {job['job_title']} at {job['company_name']}")
        print(f"   Score: {score}% | Sector: {job['sector']} | Type: {job['job_category']}")
        print(f"   Location: {job['location']}")
        print()
else:
    print(f"❌ Error: {queue_response.status_code}")
    print(queue_response.text)
