"""Fetch 165 anti-scam open data and dashboard resources."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import requests
import urllib3

# Suppress InsecureRequestWarning from police websites' SSL configurations
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DATASET_DOMAINS_PAGE = "https://data.gov.tw/dataset/176455"
DATASET_RUMORS_PAGE = "https://data.gov.tw/dataset/38262"

DEFAULT_CSV_DOMAINS_URL = (
    "https://opdadm.moi.gov.tw/api/v1/no-auth/resource/api/dataset/"
    "29E8E643-88ED-4952-B21E-BD42A3B7108C/resource/AF8F641E-B64A-4538-B457-8F7512990278/download"
)
DEFAULT_CSV_RUMORS_URL = (
    "https://opdadm.moi.gov.tw/api/v1/no-auth/resource/api/dataset/"
    "4F4DF9A5-DF4C-4EE8-A50D-869347D38D9E/resource/0E342DF7-C69A-4942-98A4-8A4D91F77705/download"
)


def get_csv_url_from_dataset_page(page_url: str, fallback_url: str) -> str:
    """Scrapes data.gov.tw dataset page to find the current CSV download URL from JSON-LD."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }
        # Disable verification because data.gov.tw or MOI servers might have minor certificate configuration anomalies
        response = requests.get(page_url, headers=headers, verify=False, timeout=15)
        response.raise_for_status()

        html = response.text
        # Search for Schema.org JSON-LD Dataset representation
        json_ld_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
        for ld_str in json_ld_matches:
            try:
                ld_data = json.loads(ld_str)
                if isinstance(ld_data, list):
                    datasets = ld_data
                else:
                    datasets = [ld_data]

                for ds in datasets:
                    if ds.get("@type") == "Dataset" or "@context" in ds:
                        distributions = ds.get("distribution", [])
                        for dist in distributions:
                            if dist.get("encodingFormat") == "CSV" and dist.get("contentUrl"):
                                return dist.get("contentUrl")
            except Exception:
                continue
    except Exception as e:
        print(f"Warning: Failed to parse dynamic CSV URL from {page_url} ({e}). Using fallback.")
    return fallback_url


def fetch_file(url: str, output_path: Path) -> None:
    """Helper to download a file from a URL to a path."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, verify=False, timeout=30)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    print(f"Successfully downloaded {url} -> {output_path}")


def fetch_dashboard_api(api_path: str, output_path: Path) -> None:
    """Fetches a JSON resource from the 165 dashboard API using GET."""
    url = f"https://165dashboard.tw/CIB_DWS_API/api/{api_path}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        response.raise_for_status()
        output_path.write_bytes(response.content)
        print(f"Successfully fetched dashboard API: {api_path} -> {output_path}")
    except Exception as e:
        print(f"Error fetching dashboard API {api_path}: {e}")
        # Write empty template structure if it fails
        output_path.write_text(json.dumps({"body": [], "code": "ERROR", "message": str(e)}), encoding="utf-8")


def fetch_all_data(raw_dir: Path) -> None:
    """Executes the full data collection pipeline."""
    raw_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fetch Stop-Resolved Scam Domains CSV
    domains_csv_url = os.getenv("ANTI_SCAM_CSV_URL")
    if not domains_csv_url:
        print("Finding latest stop-resolved domains CSV URL dynamically...")
        domains_csv_url = get_csv_url_from_dataset_page(DATASET_DOMAINS_PAGE, DEFAULT_CSV_DOMAINS_URL)
    print(f"Domains CSV URL: {domains_csv_url}")
    fetch_file(domains_csv_url, raw_dir / "165_scam_domains.csv")

    # 2. Fetch Rumor/Clarification CSV
    rumors_csv_url = get_csv_url_from_dataset_page(DATASET_RUMORS_PAGE, DEFAULT_CSV_RUMORS_URL)
    print(f"Rumors CSV URL: {rumors_csv_url}")
    fetch_file(rumors_csv_url, raw_dir / "165_rumors.csv")

    # 3. Fetch 165 Dashboard API endpoints
    # - Daily method rankings & stats
    fetch_dashboard_api("Dashboard/GetDailyFraudMethodRanking", raw_dir / "dashboard_ranking.json")
    # - Today's fraud method detailed description list
    fetch_dashboard_api("FraudMethod/GetTodayFraudMethodList", raw_dir / "today_fraud_methods.json")
    # - News marquee / tickers
    fetch_dashboard_api("NewsTicker/GetNewsTicker", raw_dir / "news_ticker.json")
    # - Daily real cases study list
    fetch_dashboard_api("CaseStudy/GetDailyCaseStudyList", raw_dir / "daily_cases.json")
