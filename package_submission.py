"""
Automated Submission Packaging Script.
Bundles the complete codebase, benchmarks, evaluation results, figures,
documentation, and formal research report into a clean, verified distribution archive.
Computes SHA256 checksums and generates SUBMISSION_MANIFEST.txt.
"""

import os
import sys
import zipfile
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_OUTPUT = os.path.join(BASE_DIR, "code_plagiarism_detection_submission.zip")
MANIFEST_TXT = os.path.join(BASE_DIR, "SUBMISSION_MANIFEST.txt")

INCLUDED_PATTERNS = [
    "baseline/",
    "ast_engine/",
    "multilang/",
    "visualizer/",
    "dataset/benchmarks/",
    "dataset/build_dataset.py",
    "dataset/validate_dataset.py",
    "dataset/ground_truth.json",
    "dataset/README.md",
    "tests/",
    "results/",
    "eval.py",
    "cli.py",
    "benchmark_jplag.py",
    "README.md",
    "SUBMISSION_MANIFEST.txt"
]

EXCLUDE_PATTERNS = ["__pycache__", ".pyc", ".zip", "jplag.jar"]

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def package():
    print("Collecting files for submission package...")
    files_to_pack = []

    for root, dirs, files in os.walk(BASE_DIR):
        # Filter pycache
        if "__pycache__" in root or ".git" in root:
            continue
        for file in files:
            rel = os.path.relpath(os.path.join(root, file), BASE_DIR).replace("\\", "/")
            if any(exc in rel for exc in EXCLUDE_PATTERNS):
                continue
            # Include files matching our directories
            if any(rel.startswith(pat) or rel == pat for pat in INCLUDED_PATTERNS):
                files_to_pack.append(rel)

    # Generate Manifest
    files_to_pack = sorted(files_to_pack)
    manifest_lines = [
        "================================================================================",
        "  PROJECT P10 SUBMISSION MANIFEST: CODE PLAGIARISM & AI EVASION DETECTION",
        "================================================================================",
        f"Total Packaged Files: {len(files_to_pack) + 1}",
        "SHA-256 Checksums:",
        "-" * 80
    ]

    for rel in files_to_pack:
        full_p = os.path.join(BASE_DIR, rel)
        csum = compute_sha256(full_p)
        manifest_lines.append(f"{csum}  {rel}")

    with open(MANIFEST_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(manifest_lines) + "\n")

    files_to_pack.append("SUBMISSION_MANIFEST.txt")

    print(f"Creating archive {ZIP_OUTPUT} with {len(files_to_pack)} files...")
    if os.path.exists(ZIP_OUTPUT):
        os.remove(ZIP_OUTPUT)

    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in files_to_pack:
            full_p = os.path.join(BASE_DIR, rel)
            arcname = os.path.join("code_plagiarism_detection", rel)
            zf.write(full_p, arcname)

    archive_size_kb = os.path.getsize(ZIP_OUTPUT) / 1024
    print(f"\nSUCCESS: Submission archive created: {ZIP_OUTPUT} ({archive_size_kb:.1f} KB)")
    print(f"Manifest written to: {MANIFEST_TXT}")

if __name__ == "__main__":
    package()
