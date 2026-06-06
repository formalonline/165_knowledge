"""Validate generated files."""
from pathlib import Path

REQUIRED_FILES = [
    "data/processed/scam-domains.csv",
    "data/processed/scam-domains.json",
    "data/processed/rumors.csv",
    "data/processed/rumors.json",
    "knowledge/anti-scam-latest.md",
    "knowledge/suspicious-domains.md",
    "knowledge/anti-scam-agent-prompt.md",
    "knowledge/scam-patterns.md",
    "knowledge/report-guide.md",
]


def validate_outputs(root: Path) -> None:
    missing = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing:
        raise RuntimeError(f"Missing output files: {missing}")
    print("Validation passed successfully. All files generated.")
