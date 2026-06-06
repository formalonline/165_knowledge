"""Normalize suspected scam domain and rumor datasets."""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

TZ_TAIPEI = timezone(timedelta(hours=8))

DOMAIN_COLUMN_CANDIDATES = {
    "year_month_roc": ["民國年月", "年月", "年月份"],
    "raw_domain": ["網域", "網址", "網域名稱", "domain", "url"],
    "site_type": ["網站性質", "類型", "site_type"],
    "legal_basis": ["法律依據", "依據"],
    "requesting_agency": ["聲請單位", "申請單位", "requesting_agency"],
}

RUMOR_COLUMN_CANDIDATES = {
    "id": ["編號", "Id", "id"],
    "title": ["標題", "Title", "title", "subject"],
    "publish_time": ["發佈時間", "發布時間", "時間", "PublishDate", "publish_time", "date"],
    "content": ["發佈內容", "發布內容", "內容", "Content", "content", "body"],
}


def pick_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def extract_domain(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    if "://" not in text:
        text_for_parse = "http://" + text
    else:
        text_for_parse = text
    parsed = urlparse(text_for_parse)
    host = parsed.netloc or parsed.path
    host = host.split("/")[0].split(":")[0].strip().lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def normalize_domains_dataset(raw_csv: Path, output_csv: Path, output_json: Path, now_str: str) -> None:
    if not raw_csv.exists():
        print(f"Warning: {raw_csv} does not exist, skipping domain normalization.")
        return

    df = pd.read_csv(raw_csv, dtype=str, encoding="utf-8-sig")
    mapped = {
        key: pick_column(df, candidates) for key, candidates in DOMAIN_COLUMN_CANDIDATES.items()
    }

    raw_domain_col = mapped["raw_domain"]
    if not raw_domain_col:
        raise ValueError(f"Cannot find domain/url column in domains dataset. Columns: {list(df.columns)}")

    out = pd.DataFrame()
    out["year_month_roc"] = df[mapped["year_month_roc"]] if mapped["year_month_roc"] else ""
    out["raw_domain"] = df[raw_domain_col].fillna("")
    out["domain"] = out["raw_domain"].apply(extract_domain)
    out["site_type"] = df[mapped["site_type"]] if mapped["site_type"] else ""
    out["legal_basis"] = df[mapped["legal_basis"]] if mapped["legal_basis"] else ""
    out["requesting_agency"] = df[mapped["requesting_agency"]] if mapped["requesting_agency"] else ""
    out["source"] = "https://data.gov.tw/dataset/176455"
    out["updated_at"] = now_str

    out = out[out["domain"] != ""].drop_duplicates(subset=["domain"]).sort_values("domain")
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_csv, index=False, encoding="utf-8-sig")

    payload = {
        "metadata": {
            "generated_at": now_str,
            "source": "https://data.gov.tw/dataset/176455",
            "record_count": int(len(out)),
        },
        "records": out.to_dict(orient="records"),
    }
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Normalized {len(out)} domain records.")


def normalize_rumors_dataset(raw_csv: Path, output_csv: Path, output_json: Path, now_str: str) -> None:
    if not raw_csv.exists():
        print(f"Warning: {raw_csv} does not exist, skipping rumor normalization.")
        return

    df = pd.read_csv(raw_csv, dtype=str, encoding="utf-8-sig")
    mapped = {
        key: pick_column(df, candidates) for key, candidates in RUMOR_COLUMN_CANDIDATES.items()
    }

    title_col = mapped["title"]
    if not title_col:
        raise ValueError(f"Cannot find title column in rumors dataset. Columns: {list(df.columns)}")

    out = pd.DataFrame()
    out["id"] = df[mapped["id"]] if mapped["id"] else ""
    out["title"] = df[title_col].fillna("").str.strip()
    out["publish_time"] = df[mapped["publish_time"]].fillna("") if mapped["publish_time"] else ""
    out["content"] = df[mapped["content"]].fillna("").str.strip() if mapped["content"] else ""
    out["source"] = "https://data.gov.tw/dataset/38262"
    out["updated_at"] = now_str

    # De-duplicate by title
    out = out[out["title"] != ""].drop_duplicates(subset=["title"])

    # Attempt to sort by publish_time desc if possible
    try:
        # Taiwan date format might be ROC year, e.g. "112/05/06" or standard YYYY-MM-DD
        # Let's try standard parsing or keep it simple
        out["parsed_time"] = pd.to_datetime(out["publish_time"], errors="coerce")
        out = out.sort_values("parsed_time", ascending=False).drop(columns=["parsed_time"])
    except Exception:
        pass

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_csv, index=False, encoding="utf-8-sig")

    payload = {
        "metadata": {
            "generated_at": now_str,
            "source": "https://data.gov.tw/dataset/38262",
            "record_count": int(len(out)),
        },
        "records": out.to_dict(orient="records"),
    }
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Normalized {len(out)} rumor records.")


def normalize_all(raw_dir: Path, processed_dir: Path) -> None:
    now_str = datetime.now(TZ_TAIPEI).isoformat(timespec="seconds")
    processed_dir.mkdir(parents=True, exist_ok=True)

    normalize_domains_dataset(
        raw_dir / "165_scam_domains.csv",
        processed_dir / "scam-domains.csv",
        processed_dir / "scam-domains.json",
        now_str
    )

    normalize_rumors_dataset(
        raw_dir / "165_rumors.csv",
        processed_dir / "rumors.csv",
        processed_dir / "rumors.json",
        now_str
    )
