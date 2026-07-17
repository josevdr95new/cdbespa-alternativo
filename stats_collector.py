#!/usr/bin/env python3
"""
GitHub Repository Lifetime Stats Collector
- Fetches traffic/views, clones from GitHub API
- Accumulates daily data into a JSON history file (lifetime stats)
- Generates a compact markdown snippet for README with badges & summary
"""

import json
import os
import sys
import datetime

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO_OWNER = os.environ.get("REPO_OWNER", "josevdr95new")
REPO_NAME = os.environ.get("REPO_NAME", "cdbespa-alternativo")
REPO_FULL = f"{REPO_OWNER}/{REPO_NAME}"
STATS_FILE = "stats_history.json"
README_STATS_FILE = "README_stats.md"
STATS_MARKER_START = "<!-- STATS:START -->"
STATS_MARKER_END = "<!-- STATS:END -->"

# ── Helper: call GitHub API ────────────────────────────────────────────────
def api_get(endpoint):
    import urllib.request
    url = f"https://api.github.com{endpoint}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"API call failed for {endpoint}: {e}", file=sys.stderr)
        return None

# ── 1. Fetch current traffic data ──────────────────────────────────────────
def fetch_traffic():
    views = api_get(f"/repos/{REPO_FULL}/traffic/views") or {"count": 0, "uniques": 0, "views": []}
    clones = api_get(f"/repos/{REPO_FULL}/traffic/clones") or {"count": 0, "uniques": 0, "clones": []}
    return views, clones

# ── 2. Fetch repo metadata ─────────────────────────────────────────────────
def fetch_repo_meta():
    repo = api_get(f"/repos/{REPO_FULL}")
    if not repo:
        return {}
    return {
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "watchers": repo.get("subscribers_count", 0),
        "open_issues": repo.get("open_issues_count", 0),
        "created_at": repo.get("created_at", ""),
    }

# ── 3. Accumulate history ──────────────────────────────────────────────────
def accumulate_history(views_data, clones_data, history):
    for key in ["daily_views", "daily_clones"]:
        if key not in history:
            history[key] = {}
    for key in ["lifetime_total_views", "lifetime_total_unique_views",
                 "lifetime_total_clones", "lifetime_total_unique_clones"]:
        if key not in history:
            history[key] = 0

    for entry in views_data.get("views", []):
        day = entry["timestamp"][:10]
        if day not in history["daily_views"]:
            history["daily_views"][day] = {"count": entry["count"], "uniques": entry["uniques"]}
        else:
            history["daily_views"][day]["count"] = max(history["daily_views"][day]["count"], entry["count"])
            history["daily_views"][day]["uniques"] = max(history["daily_views"][day]["uniques"], entry["uniques"])

    for entry in clones_data.get("clones", []):
        day = entry["timestamp"][:10]
        if day not in history["daily_clones"]:
            history["daily_clones"][day] = {"count": entry["count"], "uniques": entry["uniques"]}
        else:
            history["daily_clones"][day]["count"] = max(history["daily_clones"][day]["count"], entry["count"])
            history["daily_clones"][day]["uniques"] = max(history["daily_clones"][day]["uniques"], entry["uniques"])

    history["lifetime_total_views"] = sum(d["count"] for d in history["daily_views"].values())
    history["lifetime_total_unique_views"] = sum(d["uniques"] for d in history["daily_views"].values())
    history["lifetime_total_clones"] = sum(d["count"] for d in history["daily_clones"].values())
    history["lifetime_total_unique_clones"] = sum(d["uniques"] for d in history["daily_clones"].values())

    today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    history["last_updated"] = today_str
    return history

# ── 4. Generate compact README snippet ─────────────────────────────────────
def generate_stats_snippet(history, meta):
    tv = history.get("lifetime_total_views", 0)
    tuv = history.get("lifetime_total_unique_views", 0)
    tc = history.get("lifetime_total_clones", 0)
    tuc = history.get("lifetime_total_unique_clones", 0)
    stars = meta.get("stars", 0)
    forks = meta.get("forks", 0)
    watchers = meta.get("watchers", 0)
    last_updated = history.get("last_updated", "?")

    b = "https://img.shields.io/badge"

    lines = [
        f"{STATS_MARKER_START}",
        f"## 📊 Estadísticas",
        f"",
        f"![Visitas]({b}/Visitas-{tv}-blue) ![Visitantes únicos]({b}/Visitantes_únicos-{tuv}-brightgreen) ![Clonaciones]({b}/Clonaciones-{tc}-green) ![Stars]({b}/⭐_Stars-{stars}-ff69b4) ![Forks]({b}/Forks-{forks}-orange) ![Watchers]({b}/Watchers-{watchers}-9cf)",
        f"",
        f"| Métrica | Total | Únicos |",
        f"|---------|------:|-------:|",
        f"| 👁️ Visitas | **{tv}** | **{tuv}** |",
        f"| 🌀 Clonaciones | **{tc}** | **{tuc}** |",
        f"| ⭐ Stars | **{stars}** | — |",
        f"| 🍴 Forks | **{forks}** | — |",
        f"| 👀 Watchers | **{watchers}** | — |",
        f"",
        f"<sub>Actualizado: {last_updated} · Datos acumulados de por vida</sub>",
        f"",
        f"{STATS_MARKER_END}",
    ]
    return "\n".join(lines)

# ── 5. Inject stats into README ────────────────────────────────────────────
def inject_stats_into_readme(readme_content, stats_snippet):
    if STATS_MARKER_START in readme_content and STATS_MARKER_END in readme_content:
        # Replace existing stats block
        start_idx = readme_content.index(STATS_MARKER_START)
        end_idx = readme_content.index(STATS_MARKER_END) + len(STATS_MARKER_END)
        return readme_content[:start_idx] + stats_snippet + readme_content[end_idx:]
    else:
        # First time: append at the end
        return readme_content.rstrip() + "\n\n" + stats_snippet

# ── Main ────────────────────────────────────────────────────────────────────
def main():
    print(f"Recopilando estadísticas para {REPO_FULL}...")

    views_data, clones_data = fetch_traffic()
    meta = fetch_repo_meta()

    history = {}
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            history = json.load(f)
        print(f"Historial cargado: {len(history.get('daily_views',{}))} días")

    history = accumulate_history(views_data, clones_data, history)
    print(f"Actualizado — Visitas: {history['lifetime_total_views']}, Clonaciones: {history['lifetime_total_clones']}")

    with open(STATS_FILE, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print(f"{STATS_FILE} guardado")

    # Generate snippet
    snippet = generate_stats_snippet(history, meta)
    with open(README_STATS_FILE, "w") as f:
        f.write(snippet)
    print(f"{README_STATS_FILE} generado")

    # Inject directly into README.md
    if os.path.exists("README.md"):
        with open("README.md", "r") as f:
            readme = f.read()
        new_readme = inject_stats_into_readme(readme, snippet)
        with open("README.md", "w") as f:
            f.write(new_readme)
        print("README.md actualizado con stats")

if __name__ == "__main__":
    main()
