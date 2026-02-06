#!/usr/bin/env python3
"""
API Gateway Test Suite
Tests all endpoints for Projects 1, 2, and 3
"""

import requests
import json
from datetime import datetime
import os

# Configuration
GATEWAY_URL = "https://lean-hub-gateway-6bbg4rzf.uc.gateway.dev"

# Firebase configuration
FIREBASE_API_KEY = "AIzaSyArB51Zp5n0tsHOa7-KRzmLheHSMciTyus"  # Your Firebase Web API Key
FIREBASE_AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"

# User credentials
FIREBASE_EMAIL = "shehapkhalil62@gmail.com"
FIREBASE_PASSWORD = "123456"

# Test endpoints
ENDPOINTS = {
    "Project 1 (via Gateway)": [
        "/p1",
        "/p1/health",
        "/p1/version",
        "/p1/lib-info"
    ],
    "Project 2 (via Gateway)": [
        "/p2",
        "/p2/health",
        "/p2/version",
        "/p2/lib-info"
    ],
    "Project 3 (via Gateway)": [
        "/p3",
        "/p3/health",
        "/p3/version",
        "/p3/lib-info"
    ]
}

# Direct Cloud Run URLs (for comparison)
DIRECT_URLS = {
    "Project 1 (Direct)": "https://project-1-lkkj3foq7q-uc.a.run.app",
    "Project 3 (Direct)": "https://project-3-lkkj3foq7q-uc.a.run.app"
}

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}\n")

def print_result(status_code, success):
    """Print status with color"""
    if success:
        return f"{Colors.GREEN}✓ {status_code}{Colors.END}"
    elif status_code == 401:
        return f"{Colors.YELLOW}⚠ {status_code} (Auth Required){Colors.END}"
    else:
        return f"{Colors.RED}✗ {status_code}{Colors.END}"

def get_firebase_token(email, password, api_key):
    """Authenticate with Firebase and get ID token"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🔐 Authenticating with Firebase...{Colors.END}")
    print(f"{Colors.CYAN}Email:{Colors.END} {email}")
    
    if not api_key:
        print(f"{Colors.RED}Error:{Colors.END} FIREBASE_WEB_API_KEY not set")
        print(f"{Colors.YELLOW}Hint:{Colors.END} Set the FIREBASE_WEB_API_KEY environment variable")
        print(f"{Colors.YELLOW}      or update it directly in the script{Colors.END}")
        return None
    
    auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(auth_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("idToken")
            print(f"{Colors.GREEN}✓ Authentication successful{Colors.END}")
            print(f"{Colors.CYAN}Token (first 20 chars):{Colors.END} {token[:20]}...")
            print(f"{Colors.CYAN}User ID:{Colors.END} {data.get('localId')}")
            return token
        else:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", "Unknown error")
            print(f"{Colors.RED}✗ Authentication failed:{Colors.END} {error_msg}")
            print(f"{Colors.YELLOW}Response:{Colors.END} {json.dumps(error_data, indent=2)}")
            return None
    
    except Exception as e:
        print(f"{Colors.RED}✗ Authentication error:{Colors.END} {str(e)}")
        return None


def test_endpoint(url, auth_token=None):
    """Test a single endpoint"""
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        success = response.status_code == 200
        
        result = {
            "status_code": response.status_code,
            "success": success,
            "response": None,
            "error": None
        }
        
        # Try to parse JSON response
        try:
            result["response"] = response.json()
        except:
            result["response"] = response.text[:200]  # First 200 chars
        
        return result
    
    except requests.exceptions.Timeout:
        return {
            "status_code": "TIMEOUT",
            "success": False,
            "response": None,
            "error": "Request timed out"
        }
    except requests.exceptions.ConnectionError:
        return {
            "status_code": "CONNECTION_ERROR",
            "success": False,
            "response": None,
            "error": "Could not connect to server"
        }
    except Exception as e:
        return {
            "status_code": "ERROR",
            "success": False,
            "response": None,
            "error": str(e)
        }

def run_tests(auth_token=None):
    """Run all tests"""
    print_header(f"🧪 Testing API Gateway - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BOLD}Gateway URL:{Colors.END} {GATEWAY_URL}")
    
    if auth_token:
        print(f"{Colors.BOLD}Auth:{Colors.END} Using Firebase token")
    else:
        print(f"{Colors.BOLD}Auth:{Colors.END} No authentication (testing public access)")
    
    results = {}
    
    for project, endpoints in ENDPOINTS.items():
        print(f"\n{Colors.BOLD}{Colors.BLUE}Testing {project}:{Colors.END}")
        print("-" * 60)
        
        project_results = []
        
        for endpoint in endpoints:
            full_url = f"{GATEWAY_URL}{endpoint}"
            print(f"\n{Colors.CYAN}Endpoint:{Colors.END} {endpoint}")
            print(f"{Colors.CYAN}Full URL:{Colors.END} {full_url}")
            
            result = test_endpoint(full_url, auth_token)
            project_results.append({
                "endpoint": endpoint,
                "result": result
            })
            
            # Print status
            status = result["status_code"]
            if isinstance(status, int):
                print(f"{Colors.CYAN}Status:{Colors.END} {print_result(status, result['success'])}")
            else:
                print(f"{Colors.CYAN}Status:{Colors.END} {Colors.RED}{status}{Colors.END}")
            
            # Print response
            if result["success"]:
                if isinstance(result["response"], dict):
                    print(f"{Colors.CYAN}Response:{Colors.END}")
                    print(json.dumps(result["response"], indent=2))
                else:
                    print(f"{Colors.CYAN}Response:{Colors.END} {result['response']}")
            elif result["error"]:
                print(f"{Colors.RED}Error:{Colors.END} {result['error']}")
            elif result["response"]:
                response_str = str(result['response'])
                print(f"{Colors.YELLOW}Response:{Colors.END} {response_str[:100]}...")
        
        results[project] = project_results
    
    # Print summary
    print_header("📊 Test Summary")
    
    for project, project_results in results.items():
        successful = sum(1 for r in project_results if r["result"]["success"])
        total = len(project_results)
        
        if successful == total:
            status_icon = f"{Colors.GREEN}✓{Colors.END}"
        elif successful > 0:
            status_icon = f"{Colors.YELLOW}⚠{Colors.END}"
        else:
            status_icon = f"{Colors.RED}✗{Colors.END}"
        
        print(f"{status_icon} {Colors.BOLD}{project}:{Colors.END} {successful}/{total} passed")
    
    print()

def main():
    """Main function"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║        API Gateway Test Suite - Lean Hub              ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    # Get Firebase token
    firebase_token = get_firebase_token(FIREBASE_EMAIL, FIREBASE_PASSWORD, FIREBASE_API_KEY)
    
    if firebase_token:
        # Test Gateway endpoints with authentication
        run_tests(auth_token=firebase_token)
        
        # Also test direct Cloud Run URLs (they should be internal-only and fail)
        print(f"\n{Colors.BOLD}{Colors.BLUE}Testing Direct Cloud Run URLs (should fail - internal ingress only):{Colors.END}")
        for service, base_url in DIRECT_URLS.items():
            print(f"\n{Colors.CYAN}{service}:{Colors.END} {base_url}/health")
            result = test_endpoint(f"{base_url}/health", firebase_token)
            status = result["status_code"]
            if isinstance(status, int):
                print(f"  {print_result(status, result['success'])}")
            else:
                print(f"  {Colors.RED}{status}{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠ Proceeding without authentication (expect 401 errors){Colors.END}")
        # Test without authentication to see the behavior
        run_tests()

if __name__ == "__main__":
    main()
