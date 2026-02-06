#!/usr/bin/env python3
"""Simple test for deployed services"""

import requests

# Firebase auth
FIREBASE_API_KEY = "AIzaSyArB51Zp5n0tsHOa7-KRzmLheHSMciTyus"
email = "shehapkhalil62@gmail.com"
password = "123456"

print("🔐 Getting Firebase token...")
auth_response = requests.post(
    f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}",
    json={"email": email, "password": password, "returnSecureToken": True}
)

if auth_response.status_code == 200:
    token = auth_response.json()["idToken"]
    print(f"✓ Got token: {token[:20]}...\n")
    headers = {"Authorization": f"Bearer {token}"}
else:
    print(f"✗ Auth failed: {auth_response.json()}\n")
    headers = {}

# Test direct Cloud Run URLs (should work because of --ingress all by default, or fail if internal)
print("Testing Direct Cloud Run URLs:")
print("="*60)

services = {
    "Project 1": "https://project-1-494821814955.us-central1.run.app",
    "Project 3": "https://project-3-494821814955.us-central1.run.app"
}

for name, url in services.items():
    print(f"\n{name}: {url}")
    for endpoint in ["/", "/health", "/version"]:
        try:
            response = requests.get(f"{url}{endpoint}", headers=headers, timeout=5)
            print(f"  {endpoint:15} → {response.status_code} {response.reason}")
            if response.status_code == 200:
                try:
                    print(f"    Response: {response.json()}")
                except:
                    print(f"    Response: {response.text[:100]}")
        except Exception as e:
            print(f"  {endpoint:15} → ERROR: {e}")

# Test Gateway
print("\n\nTesting API Gateway:")
print("="*60)

gateway_url = "https://lean-hub-gateway-6bbg4rzf.uc.gateway.dev"
print(f"Gateway: {gateway_url}\n")

for project in ["p1", "p2", "p3"]:
    print(f"\nProject {project}:")
    for endpoint in ["", "/health", "/version"]:
        try:
            response = requests.get(f"{gateway_url}/{project}{endpoint}", headers=headers, timeout=5)
            print(f"  /{project}{endpoint:15} → {response.status_code} {response.reason}")
            if response.status_code == 200:
                try:
                    print(f"    Response: {response.json()}")
                except:
                    print(f"    Response: {response.text[:100]}")
        except Exception as e:
            print(f"  /{project}{endpoint:15} → ERROR: {e}")
