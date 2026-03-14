#!/usr/bin/env python3
"""
Generate OpenAPI config for API Gateway from a single service registry file.

This script reads:
  - infrastructure/services-registry.json
  - live Cloud Run service URLs via gcloud

Then writes:
  - OpenAPI JSON config usable by gcloud api-gateway api-configs create
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Dict, Any, List, Tuple


def _run_cmd(cmd: List[str]) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def _load_registry(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_cloud_run_urls(project_id: str, region: str) -> Dict[str, str]:
    cmd = [
        "gcloud",
        "run",
        "services",
        "list",
        "--region",
        region,
        "--project",
        project_id,
        "--format=json",
    ]
    rc, out, err = _run_cmd(cmd)
    if rc != 0:
        print("[WARN] Unable to list Cloud Run services. Using placeholders.")
        print(f"[WARN] gcloud stderr: {err.strip()}")
        return {}

    try:
        data = json.loads(out or "[]")
    except json.JSONDecodeError:
        print("[WARN] Invalid JSON from gcloud. Using placeholders.")
        return {}

    urls: Dict[str, str] = {}
    for item in data:
        # gcloud shape is typically metadata.name + status.url
        name = (
            item.get("metadata", {}).get("name")
            or item.get("serviceName")
            or item.get("name")
        )
        url = item.get("status", {}).get("url")
        if name and url:
            urls[name] = url
    return urls


def _join_url(base: str, suffix: str) -> str:
    if not suffix:
        return base
    if suffix.startswith("/"):
        return f"{base}{suffix}"
    return f"{base}/{suffix}"


def _build_openapi(
    registry: Dict[str, Any], firebase_project_id: str, url_map: Dict[str, str]
) -> Tuple[Dict[str, Any], List[Tuple[str, str]]]:
    gateway = registry["gateway"]
    services = registry["services"]

    paths: Dict[str, Any] = {}
    resolved: List[Tuple[str, str]] = []

    for svc in services:
        sid = svc["id"]
        service_name = svc["service_name"]
        placeholder = svc["placeholder_url"]
        base_url = url_map.get(service_name, placeholder)
        resolved.append((service_name, base_url))

        prefix = f"/{sid}"
        for route in svc["routes"]:
            suffix = route.get("path_suffix", "")
            method = route["method"].lower()
            full_path = f"{prefix}{suffix}"
            backend_address = _join_url(base_url, suffix)

            if full_path not in paths:
                paths[full_path] = {}

            paths[full_path][method] = {
                "summary": route["summary"],
                "operationId": route["operation_id"],
                "x-google-backend": {
                    "address": backend_address,
                    "path_translation": "CONSTANT_ADDRESS",
                },
                "responses": {
                    "200": {"description": route.get("response_description", "OK")}
                },
            }

    openapi = {
        "swagger": "2.0",
        "info": {
            "title": gateway["title"],
            "description": gateway["description"],
            "version": gateway["version"],
        },
        "host": gateway["host"],
        "schemes": ["https"],
        "securityDefinitions": {
            "firebase": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-issuer": f"https://securetoken.google.com/{firebase_project_id}",
                "x-google-jwks_uri": "https://www.googleapis.com/service_accounts/v1/metadata/x509/securetoken@system.gserviceaccount.com",
                "x-google-audiences": firebase_project_id,
            }
        },
        "security": [{"firebase": []}],
        "paths": paths,
    }
    return openapi, resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--project-id", default=os.getenv("GCP_PROJECT_ID", ""))
    parser.add_argument("--region", default=os.getenv("GCP_REGION", "us-central1"))
    parser.add_argument(
        "--firebase-project-id", default=os.getenv("FIREBASE_PROJECT_ID", "")
    )
    args = parser.parse_args()

    if not args.project_id:
        print("[ERROR] Missing project id. Set GCP_PROJECT_ID or pass --project-id.")
        return 1
    if not args.firebase_project_id:
        print(
            "[ERROR] Missing Firebase project id. Set FIREBASE_PROJECT_ID or pass --firebase-project-id."
        )
        return 1

    registry = _load_registry(args.registry)
    url_map = _load_cloud_run_urls(args.project_id, args.region)
    openapi, resolved = _build_openapi(registry, args.firebase_project_id, url_map)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(openapi, f, indent=2)

    print("[INFO] API Gateway OpenAPI config generated.")
    print(f"[INFO] Output: {args.output}")
    print("[INFO] Resolved backend base URLs:")
    for service_name, url in resolved:
        print(f"  - {service_name}: {url}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
