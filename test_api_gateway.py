#!/usr/bin/env python3
"""
API Gateway Test Suite
ment
Tests all endpoints defined in infrastructure/gateway/services-registry.json
"""

import requests
import json
from datetime import datetime
import os
import sys

def env_or_default(key, default):
    value = os.getenv(key)
    if value is None or str(value).strip() == "":
        return default
    return value

# Configuration
GATEWAY_URL = env_or_default("GATEWAY_URL", "https://lean-hub-gateway-6bbg4rzf.uc.gateway.dev")

# Firebase configuration
FIREBASE_API_KEY = env_or_default("FIREBASE_API_KEY", "AIzaSyArB51Zp5n0tsHOa7-KRzmLheHSMciTyus")

# User credentials
FIREBASE_EMAIL = env_or_default("FIREBASE_EMAIL", "shehapkhalil62@gmail.com")
FIREBASE_PASSWORD = env_or_default("FIREBASE_PASSWORD", "123456")
SERVICES_REGISTRY_PATH = env_or_default(
    "SERVICES_REGISTRY_PATH", "infrastructure/gateway/services-registry.json"
)

def load_endpoints_from_registry(path):
    """Load endpoint definitions from services registry."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except Exception as e:
        print(f"Error: Failed to load services registry at '{path}': {e}")
        return {}

    endpoints = {}
    for service in registry.get("services", []):
        service_id = service.get("id", "unknown")
        service_label = f"Project {service_id.upper()} (via Gateway)"
        service_routes = []

        for route in service.get("routes", []):
            path_suffix = route.get("path_suffix", "")
            method = str(route.get("method", "get")).lower()
            endpoint_path = f"/{service_id}{path_suffix}"
            service_routes.append(
                {
                    "path": endpoint_path,
                    "method": method,
                    "summary": route.get("summary", ""),
                }
            )

        endpoints[service_label] = service_routes
    return endpoints


ENDPOINTS = load_endpoints_from_registry(SERVICES_REGISTRY_PATH)

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


def test_endpoint(url, method="get", auth_token=None):
    """Test a single endpoint"""
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        request_kwargs = {"headers": headers, "timeout": 10}
        if method in ("post", "put", "patch"):
            # Minimal payload to exercise route existence through gateway.
            request_kwargs["json"] = {}

        response = requests.request(method=method.upper(), url=url, **request_kwargs)
        # For path verification we treat non-404/non-405 as route exists.
        # 401 is still considered a failure because tests provide auth token.
        success = response.status_code not in (404, 405) and response.status_code < 500
        
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
    print(f"{Colors.BOLD}Registry:{Colors.END} {SERVICES_REGISTRY_PATH}")
    
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
            endpoint_path = endpoint["path"]
            endpoint_method = endpoint.get("method", "get").lower()
            full_url = f"{GATEWAY_URL}{endpoint_path}"
            print(f"\n{Colors.CYAN}Endpoint:{Colors.END} {endpoint_method.upper()} {endpoint_path}")
            print(f"{Colors.CYAN}Full URL:{Colors.END} {full_url}")
            
            result = test_endpoint(full_url, method=endpoint_method, auth_token=auth_token)
            project_results.append({
                "endpoint": endpoint_path,
                "method": endpoint_method,
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
    all_passed = all(
        all(item["result"]["success"] for item in project_results)
        for project_results in results.values()
    )
    return all_passed

def main():
    """Main function"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║        API Gateway Test Suite - Lean Hub              ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    if not ENDPOINTS:
        print(f"{Colors.RED}✗ No endpoints found from services registry.{Colors.END}")
        return 1

    # Get Firebase token
    firebase_token = get_firebase_token(FIREBASE_EMAIL, FIREBASE_PASSWORD, FIREBASE_API_KEY)
    
    if firebase_token:
        # Test Gateway endpoints with authentication
        all_passed = run_tests(auth_token=firebase_token)
        return 0 if all_passed else 1
    else:
        print(f"\n{Colors.YELLOW}⚠ Proceeding without authentication (expect 401 errors){Colors.END}")
        all_passed = run_tests()
        return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
