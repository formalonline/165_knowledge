"""Run the full anti-scam knowledge update pipeline."""
from pathlib import Path

from fetch_165_open_data import fetch_all_data
from generate_markdown import generate_all_markdown
from normalize_domains import normalize_all
from validate_output import validate_outputs

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    raw_dir = ROOT / "data" / "raw"
    processed_dir = ROOT / "data" / "processed"
    knowledge_dir = ROOT / "knowledge"

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    knowledge_dir.mkdir(parents=True, exist_ok=True)

    print("Step 1: Fetching all datasets and dashboard APIs...")
    fetch_all_data(raw_dir)

    print("Step 2: Normalizing datasets...")
    normalize_all(raw_dir, processed_dir)

    print("Step 3: Generating AI-readable Markdown files...")
    processed_csv = processed_dir / "scam-domains.csv"
    processed_json = processed_dir / "scam-domains.json"
    generate_all_markdown(processed_csv, processed_json, knowledge_dir)

    print("Step 4: Validating output files...")
    validate_outputs(ROOT)

    print("Update completed successfully.")


if __name__ == "__main__":
    main()
