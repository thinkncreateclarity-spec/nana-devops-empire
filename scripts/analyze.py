#!/usr/bin/env python3
import csv
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def run(cmd, cwd=None):
    return subprocess.check_output(
        cmd, cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def git_root():
    return Path(run(["git", "rev-parse", "--show-toplevel"]))


def git_lines(args, root):
    out = run(["git"] + args, cwd=root)
    return [x for x in out.splitlines() if x.strip()]


def scan_all_files(root):
    return [p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]


def relpath(path, root):
    try:
        return str(path.relative_to(root))
    except Exception:
        return str(path)


def classify(path):
    ext = path.suffix.lower()
    return {
        ".py": "Python",
        ".sh": "Shell",
        ".md": "Markdown",
        ".json": "JSON",
        ".toml": "TOML",
        ".yml": "YAML",
        ".yaml": "YAML",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".kt": "Kotlin",
        ".java": "Java",
        ".c": "C",
        ".h": "C/C++ Header",
        ".cpp": "C++",
        ".rb": "Ruby",
        ".go": "Go",
        ".rs": "Rust",
        ".sql": "SQL",
        ".txt": "Text",
    }.get(ext, "Other")


def health(score):
    return "healthy" if score < 0.25 else "watch" if score < 0.5 else "attention"


def compute_score(ignored, untracked, dirty, md_count, commits):
    s = 0.0
    s += min(0.25, ignored / 200.0)
    s += min(0.20, untracked / 200.0)
    s += min(0.15, dirty / 100.0)
    if md_count == 0:
        s += 0.10
    if len(commits) < 3:
        s += 0.10
    return round(min(s, 1.0), 3)


def main():
    root = git_root()
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    ts = datetime.now(timezone.utc).isoformat()

    all_files = scan_all_files(root)
    tracked = set(Path(root, p) for p in git_lines(["ls-files"], root))
    untracked = [Path(root, p) for p in git_lines(["ls-files", "--others", "--exclude-standard"], root)]
    ignored = [Path(root, p) for p in git_lines(["ls-files", "--others", "--ignored", "--exclude-standard"], root)]
    dirty = git_lines(["status", "--short"], root)
    commits = git_lines(["log", "-n10", "--oneline"], root)

    ext_counts = Counter()
    lang_counts = Counter()
    folder_counts = Counter()

    for p in all_files:
        ext_counts[p.suffix.lower() or "[no_ext]"] += 1
        lang_counts[classify(p)] += 1
        parts = p.relative_to(root).parts
        folder_counts[parts[0] if len(parts) > 1 else "."] += 1

    total = len(all_files)
    tracked_n = sum(1 for p in all_files if p in tracked)
    untracked_n = len([p for p in untracked if p.is_file()])
    ignored_n = len([p for p in ignored if p.is_file()])
    top_lang = lang_counts.most_common(1)[0][0] if lang_counts else "Unknown"

    # Base score from existing heuristics
    base_score = compute_score(
        ignored_n,
        untracked_n,
        len(dirty),
        ext_counts.get(".md", 0),
        commits,
    )

    # Smarter risk: derive flags from existing counts
    risk_flags = {}
    untracked_ratio = untracked_n / total if total else 0.0
    ignored_ratio = ignored_n / total if total else 0.0

    risk_flags["untracked_too_high"] = (
        untracked_n > 10 or untracked_ratio > 0.2
    )
    risk_flags["ignored_too_high"] = ignored_ratio > 0.4
    risk_flags["no_markdown_docs"] = ext_counts.get(".md", 0) == 0
    risk_flags["too_few_recent_commits"] = len(commits) < 3

    # Adjust score modestly based on flags
    score = base_score
    if risk_flags["untracked_too_high"]:
        score += 0.2
    if risk_flags["ignored_too_high"]:
        score += 0.1
    if risk_flags["no_markdown_docs"]:
        score += 0.1
    if risk_flags["too_few_recent_commits"]:
        score += 0.05

    score = round(min(score, 1.0), 3)
    st = health(score)

    md_lines = []
    md_lines.append("# Repo Health Report")
    md_lines.append("")
    md_lines.append(f"- Run ID: `{run_id}`")
    md_lines.append(f"- Timestamp: `{ts}`")
    md_lines.append(f"- Repo root: `{root}`")
    md_lines.append(f"- Health status: **{st}**")
    md_lines.append(f"- Risk score: **{score}**")
    md_lines.append("")
    md_lines.append("## Repo snapshot")
    md_lines.append(f"- Total files: {total}")
    md_lines.append(f"- Tracked files: {tracked_n}")
    md_lines.append(f"- Untracked files: {untracked_n}")
    md_lines.append(f"- Ignored files: {ignored_n}")
    md_lines.append("")
    md_lines.append("## Language breakdown")
    md_lines.append("| Language | Files |")
    md_lines.append("|---|---:|")
    for k, v in lang_counts.most_common():
        md_lines.append(f"| {k} | {v} |")
    md_lines.append("")
    md_lines.append("## Git activity")
    if commits:
        for c in commits:
            md_lines.append(f"- {c}")
    else:
        md_lines.append("- No commits found in the inspected window.")
    md_lines.append("")
    md_lines.append("## Narrative")
    if st == "healthy":
        md_lines.append("The repository is reasonably clean.")
    elif st == "watch":
        md_lines.append("The repository needs periodic cleanup.")
    else:
        md_lines.append("The repository shows multiple hygiene signals.")

    with open(reports / "analysis-latest.md", "w", encoding="utf-8") as f:
        for line in md_lines:
            f.write(line)
            f.write(chr(10))

    csv_path = reports / "history.csv"
    csv_exists = csv_path.exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "run_id",
                "timestamp",
                "repo_root",
                "total_files",
                "tracked_files",
                "untracked_files",
                "ignored_files",
                "top_language",
                "risk_score",
                "health_status",
            ],
        )
        if not csv_exists:
            w.writeheader()
        w.writerow(
            {
                "run_id": run_id,
                "timestamp": ts,
                "repo_root": str(root),
                "total_files": total,
                "tracked_files": tracked_n,
                "untracked_files": untracked_n,
                "ignored_files": ignored_n,
                "top_language": top_lang,
                "risk_score": score,
                "health_status": st,
            }
        )

    snap = {
        "meta": {
            "run_id": run_id,
            "timestamp": ts,
            "repo_root": str(root),
        },
        "counts": {
            "total_files": total,
            "tracked_files": tracked_n,
            "untracked_files": untracked_n,
            "ignored_files": ignored_n,
        },
        "languages": dict(lang_counts),
        "extensions": dict(ext_counts),
        "folders": dict(folder_counts),
        "git": {"dirty_count": len(dirty), "recent_commits": commits},
        "tracked": [relpath(p, root) for p in sorted(tracked)],
        "ignored": [relpath(p, root) for p in sorted(ignored)],
        "score": score,
        "status": st,
        "flags": risk_flags,
    }
    with open(reports / "risk-latest.json", "w", encoding="utf-8") as f:
        json.dump(snap, f, indent=2)
        f.write(chr(10))

    print("Wrote reports/analysis-latest.md")
    print("Wrote reports/history.csv")
    print("Wrote reports/risk-latest.json")
    print(f"Status: {st} ({score})")


if __name__ == "__main__":
    main()
