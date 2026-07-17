#!/usr/bin/env python3
"""
GitHub Repository Lifetime Stats Collector
- Fetches traffic/views, clones, referrers, paths from GitHub API
- Accumulates daily data into a JSON history file (lifetime stats)
- Generates a markdown snippet for README with badges & stats table
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
    referrers = api_get(f"/repos/{REPO_FULL}/traffic/popular/referrers") or []
    paths = api_get(f"/repos/{REPO_FULL}/traffic/popular/paths") or []
    return views, clones, referrers, paths

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
        "size_kb": repo.get("size", 0),
        "created_at": repo.get("created_at", ""),
        "language": repo.get("language", ""),
    }

# ── 3. Accumulate history ──────────────────────────────────────────────────
def accumulate_history(views_data, clones_data, history):
    # Ensure keys
    if "daily_views" not in history:
        history["daily_views"] = {}
    if "daily_clones" not in history:
        history["daily_clones"] = {}
    if "lifetime_total_views" not in history:
        history["lifetime_total_views"] = 0
    if "lifetime_total_unique_views" not in history:
        history["lifetime_total_unique_views"] = 0
    if "lifetime_total_clones" not in history:
        history["lifetime_total_clones"] = 0
    if "lifetime_total_unique_clones" not in history:
        history["lifetime_total_unique_clones"] = 0

    # Accumulate daily views (GitHub only keeps 14 days, so we store each day)
    for entry in views_data.get("views", []):
        day = entry["timestamp"][:10]
        if day not in history["daily_views"]:
            history["daily_views"][day] = {"count": entry["count"], "uniques": entry["uniques"]}
        else:
            history["daily_views"][day]["count"] = max(history["daily_views"][day]["count"], entry["count"])
            history["daily_views"][day]["uniques"] = max(history["daily_views"][day]["uniques"], entry["uniques"])

    # Same for clones
    for entry in clones_data.get("clones", []):
        day = entry["timestamp"][:10]
        if day not in history["daily_clones"]:
            history["daily_clones"][day] = {"count": entry["count"], "uniques": entry["uniques"]}
        else:
            history["daily_clones"][day]["count"] = max(history["daily_clones"][day]["count"], entry["count"])
            history["daily_clones"][day]["uniques"] = max(history["daily_clones"][day]["uniques"], entry["uniques"])

    # Recalculate lifetime totals from all daily entries
    history["lifetime_total_views"] = sum(d["count"] for d in history["daily_views"].values())
    history["lifetime_total_unique_views"] = sum(d["uniques"] for d in history["daily_views"].values())
    history["lifetime_total_clones"] = sum(d["count"] for d in history["daily_clones"].values())
    history["lifetime_total_unique_clones"] = sum(d["uniques"] for d in history["daily_clones"].values())

    today_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    history["last_updated"] = today_str
    return history

# ── 4. Generate README markdown ────────────────────────────────────────────
def generate_readme(history, meta, referrers, paths):
    total_views = history.get("lifetime_total_views", 0)
    total_unique_views = history.get("lifetime_total_unique_views", 0)
    total_clones = history.get("lifetime_total_clones", 0)
    total_unique_clones = history.get("lifetime_total_unique_clones", 0)
    stars = meta.get("stars", 0)
    forks = meta.get("forks", 0)
    watchers = meta.get("watchers", 0)
    last_updated = history.get("last_updated", "?")

    # Badge URLs
    badge_base = "https://img.shields.io/badge"
    views_badge = f"![Visitas]({badge_base}/Visitas-{total_views}-blue)"
    unique_views_badge = f"![Visitantes%20%C3%BAnicos]({badge_base}/Visitantes_%C3%BAnicos-{total_unique_views}-brightgreen)"
    clones_badge = f"![Clonaciones]({badge_base}/Clonaciones-{total_clones}-green)"
    unique_clones_badge = f"![Clonadores%20%C3%BAnicos]({badge_base}/Clonadores_%C3%BAnicos-{total_unique_clones}-yellow)"
    stars_badge = f"![Stars]({badge_base}/Stars-{stars}-ff69b4)"
    forks_badge = f"![Forks]({badge_base}/Forks-{forks}-orange)"
    watchers_badge = f"![Watchers]({badge_base}/Watchers-{watchers}-9cf)"

    lines = []
    lines.append("<!-- AUTO-GENERATED STATS — Do not edit manually. Updated by GitHub Actions -->")
    lines.append("")
    lines.append("## Estadisticas de por vida del repositorio")
    lines.append("")
    lines.append(f"{views_badge} {unique_views_badge} {clones_badge} {unique_clones_badge} {stars_badge} {forks_badge} {watchers_badge}")
    lines.append("")
    lines.append(f"> Ultima actualizacion: **{last_updated}**")
    lines.append("")
    lines.append("| Metrica | Total | Unicos |")
    lines.append("|---------|------:|-------:|")
    lines.append(f"| Visitas | **{total_views}** | **{total_unique_views}** |")
    lines.append(f"| Clonaciones | **{total_clones}** | **{total_unique_clones}** |")
    lines.append(f"| Stars | **{stars}** | — |")
    lines.append(f"| Forks | **{forks}** | — |")
    lines.append(f"| Watchers | **{watchers}** | — |")
    lines.append("")

    # Referrers section
    if referrers:
        lines.append("### Fuentes de trafico principales")
        lines.append("")
        lines.append("| Fuente | Visitas | Unicos |")
        lines.append("|--------|--------:|-------:|")
        for r in referrers[:10]:
            ref = r.get("referrer", "Directo")
            lines.append(f"| {ref} | {r.get('count',0)} | {r.get('uniques',0)} |")
        lines.append("")

    # Popular paths
    if paths:
        lines.append("### Contenido mas visitado")
        lines.append("")
        lines.append("| Ruta | Visitas | Unicos |")
        lines.append("|------|--------:|-------:|")
        for p in paths[:10]:
            path = p.get("path", "?")
            lines.append(f"| `{path}` | {p.get('count',0)} | {p.get('uniques',0)} |")
        lines.append("")

    # Daily trends (last 14 days)
    daily_views = history.get("daily_views", {})
    if daily_views:
        sorted_days = sorted(daily_views.keys(), reverse=True)[:14]
        lines.append("### Visitas diarias (ultimos 14 dias)")
        lines.append("")
        lines.append("| Fecha | Visitas | Unicos |")
        lines.append("|-------|--------:|-------:|")
        for day in sorted_days:
            d = daily_views[day]
            lines.append(f"| {day} | {d['count']} | {d['uniques']} |")
        lines.append("")

        daily_clones = history.get("daily_clones", {})
        sorted_clone_days = sorted(daily_clones.keys(), reverse=True)[:14]
        lines.append("### Clonaciones diarias (ultimos 14 dias)")
        lines.append("")
        lines.append("| Fecha | Clonaciones | Unicos |")
        lines.append("|-------|------------:|-------:|")
        for day in sorted_clone_days:
            d = daily_clones[day]
            lines.append(f"| {day} | {d['count']} | {d['uniques']} |")
        lines.append("")

    lines.append("---")
    lines.append("*Estadisticas recopiladas automaticamente mediante GitHub Actions. La API de GitHub solo retiene 14 dias de datos de trafico; este sistema los acumula para ofrecer estadisticas de por vida.*")
    lines.append("")

    return "\n".join(lines)

# ── Main ────────────────────────────────────────────────────────────────────
def main():
    print(f"Recopilando estadisticas para {REPO_FULL}...")

    # Fetch data
    views_data, clones_data, referrers, paths = fetch_traffic()
    meta = fetch_repo_meta()

    # Load existing history
    history = {}
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            history = json.load(f)
        print(f"Historial existente cargado: {len(history.get('daily_views',{}))} dias de datos")

    # Accumulate
    history = accumulate_history(views_data, clones_data, history)
    print(f"Historial actualizado — Visitas totales: {history['lifetime_total_views']}, Clonaciones totales: {history['lifetime_total_clones']}")

    # Save history
    with open(STATS_FILE, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print(f"{STATS_FILE} guardado")

    # Generate README stats snippet
    readme_md = generate_readme(history, meta, referrers, paths)
    with open(README_STATS_FILE, "w") as f:
        f.write(readme_md)
    print(f"{README_STATS_FILE} generado")

if __name__ == "__main__":
    main()
