#!/usr/bin/env python3
"""
CDBtext Auto-Migrator for CI/CD
Adapted from https://github.com/josevdr95new/CDBtext_migrator

- Clones BabelCDB (en) and IgnisMulti/Español (es)
- Transfers text fields from English CDBs into the Spanish copies
- Writes updated CDBs directly into the repo
- Generates a detailed migration log (MIGRATE_LOG.md)
- Tracks last processed SHAs to avoid unnecessary work
"""

import sqlite3
import os
import re
import json
import shutil
import subprocess
from datetime import datetime, timezone

REPO_DIR = os.environ.get("REPO_DIR", ".")
CACHE_FILE = os.path.join(REPO_DIR, ".migrate_cache.json")
MIGRATE_LOG_FILE = os.path.join(REPO_DIR, "MIGRATE_LOG.md")
BABELCDB_SHA_CACHE = "last_babelcdb_sha"
IGNIS_SHA_CACHE = "last_ignis_sha"

LOG_MARKER_START = "<!-- MIGRATE_LOG:START -->"
LOG_MARKER_END = "<!-- MIGRATE_LOG:END -->"

def replace_quoted_content(original_str, en_str):
    """Replace content inside double quotes of original_str with en_str's, preserving text outside quotes."""
    quoted_spans_es = re.findall(r'"(.*?)"', original_str)
    quoted_spans_en = re.findall(r'"(.*?)"', en_str)
    if len(quoted_spans_es) == len(quoted_spans_en):
        new_str = original_str
        for i in range(len(quoted_spans_en)):
            new_str = new_str.replace(f'"{quoted_spans_es[i]}"', f'"{quoted_spans_en[i]}"', 1)
        return new_str
    return original_str

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def get_remote_sha(repo, branch="master"):
    """Get latest commit SHA for a remote repo's branch."""
    import urllib.request
    token = os.environ.get("GITHUB_TOKEN", "")
    url = f"https://api.github.com/repos/{repo}/commits/{branch}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data.get("sha", "")
    except Exception as e:
        print(f"Error fetching SHA for {repo}: {e}")
        return ""

def clone_source_repos():
    """Clone BabelCDB and IgnisMulti to temp directories."""
    token = os.environ.get("GITHUB_TOKEN", "")
    babel_dir = "/tmp/babelcdb"
    ignis_dir = "/tmp/ignismulti"

    for d in [babel_dir, ignis_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)

    print("Cloning BabelCDB (English)...")
    babel_url = f"https://{token}@github.com/ProjectIgnis/BabelCDB.git" if token else "https://github.com/ProjectIgnis/BabelCDB.git"
    subprocess.run(["git", "clone", "--depth", "1", babel_url, babel_dir], check=True, capture_output=True)

    print("Cloning IgnisMulti (Spanish)...")
    ignis_url = f"https://{token}@github.com/Team13fr/IgnisMulti.git" if token else "https://github.com/Team13fr/IgnisMulti.git"
    subprocess.run(["git", "clone", "--depth", "1", ignis_url, ignis_dir], check=True, capture_output=True)

    return babel_dir, ignis_dir

def transfer_texts(en_folder, es_folder, repo_dir):
    """
    Transfer texts from English CDBs to Spanish CDBs.
    Returns (total_updates, log_data) where log_data contains per-file per-card details.
    """
    en_files = {f for f in os.listdir(en_folder) if f.endswith('.cdb')}
    es_files = {f for f in os.listdir(es_folder) if f.endswith('.cdb')}
    common_files = sorted(en_files & es_files)

    os.makedirs(repo_dir, exist_ok=True)

    print(f"\nCommon CDB files: {len(common_files)}")
    total_updates = 0
    all_log_data = []  # List of {"file": ..., "cards": [...]}

    for file_name in common_files:
        en_path = os.path.join(en_folder, file_name)
        es_path = os.path.join(es_folder, file_name)
        repo_path = os.path.join(repo_dir, file_name)

        shutil.copy2(es_path, repo_path)

        file_log = {"file": file_name, "cards": []}

        try:
            conn_en = sqlite3.connect(en_path)
            conn_repo = sqlite3.connect(repo_path)
            cursor_en = conn_en.cursor()
            cursor_repo = conn_repo.cursor()

            columns = ['name', '"desc"', 'str1', 'str2', 'str3', 'str4', 'str5', 'str6', 'str7']
            cursor_en.execute(f'SELECT id, {", ".join(columns)} FROM texts')
            en_texts = {row[0]: {col: row[i+1] for i, col in enumerate(columns)} for row in cursor_en.fetchall()}

            file_updates = 0
            for text_id, en_data in en_texts.items():
                cursor_repo.execute(f'SELECT {", ".join(columns)} FROM texts WHERE id = ?', (text_id,))
                es_row = cursor_repo.fetchone()

                if es_row:
                    es_data = {col: val for col, val in zip(columns, es_row)}
                    updates = {}
                    card_changes = []

                    for col in columns:
                        es_val = es_data[col]
                        en_val = en_data.get(col)

                        if col in ['"desc"', 'str1', 'str2', 'str3', 'str4', 'str5', 'str6', 'str7']:
                            if es_val and en_val:
                                new_val = replace_quoted_content(es_val, en_val)
                                if new_val != es_val:
                                    updates[col] = new_val
                                    card_changes.append({
                                        "field": col.strip('"'),
                                        "before": es_val[:80],
                                        "after": new_val[:80]
                                    })
                        else:  # 'name'
                            if en_val and en_val != es_data.get('name', ''):
                                updates[col] = en_val
                                card_changes.append({
                                    "field": "name",
                                    "before": es_data.get('name', '')[:80],
                                    "after": en_val[:80]
                                })

                    if updates:
                        set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
                        params = list(updates.values()) + [text_id]
                        cursor_repo.execute(f"UPDATE texts SET {set_clause} WHERE id = ?", params)
                        file_updates += 1
                        file_log["cards"].append({
                            "id": text_id,
                            "name": en_data.get('name', '?') if en_data.get('name') else es_data.get('name', '?'),
                            "changes": card_changes
                        })

            conn_repo.commit()
            total_updates += file_updates
            file_log["updated_count"] = file_updates
            all_log_data.append(file_log)
            print(f"  {file_name}: {file_updates} registros actualizados")

        except Exception as e:
            print(f"  ERROR en {file_name}: {e}")
            file_log["error"] = str(e)
            if conn_repo:
                conn_repo.rollback()
        finally:
            conn_en.close()
            conn_repo.close()

    # Files only in Spanish
    es_only = sorted(es_files - en_files)
    for file_name in es_only:
        src = os.path.join(es_folder, file_name)
        dst = os.path.join(repo_dir, file_name)
        shutil.copy2(src, dst)
        all_log_data.append({"file": file_name, "status": "solo español, sin migración"})
        print(f"  {file_name}: copiado (solo español)")

    # Files only in English
    en_only = sorted(en_files - es_files)
    for file_name in en_only:
        src = os.path.join(en_folder, file_name)
        dst = os.path.join(repo_dir, file_name)
        shutil.copy2(src, dst)
        all_log_data.append({"file": file_name, "status": "solo inglés, sin traducción"})
        print(f"  {file_name}: copiado (solo inglés)")

    print(f"\nTotal: {total_updates} registros actualizados en {len(common_files)} archivos")
    return total_updates, all_log_data

def generate_log_markdown(log_data, cache, babel_sha, ignis_sha, limit=None):
    """Generate a markdown migration log. If limit is set, only show that many cards per file."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"{LOG_MARKER_START}",
        f"## 🔄 Log de migración",
        f"",
        f"<sub>Última migración: **{now}**</sub>",
        f"",
        f"**Fuentes:**",
        f"- `ProjectIgnis/BabelCDB` @ `{babel_sha[:7]}`",
        f"- `Team13fr/IgnisMulti` @ `{ignis_sha[:7]}`",
        f"",
    ]

    # Summary table
    lines.append("### Resumen por archivo")
    lines.append("")
    lines.append("| Archivo | Registros migrados | Estado |")
    lines.append("|---------|-------------------:|--------|")

    total_migrated = 0
    for entry in log_data:
        fname = entry["file"]
        if "error" in entry:
            lines.append(f"| `{fname}` | — | ❌ Error |")
        elif "status" in entry:
            lines.append(f"| `{fname}` | 0 | 📋 {entry['status']} |")
        else:
            count = entry.get("updated_count", 0)
            total_migrated += count
            lines.append(f"| `{fname}` | **{count}** | ✅ Migrado |")

    lines.append(f"| **Total** | **{total_migrated}** | |")
    lines.append("")

    # Detailed per-file logs
    max_show = limit  # None means show all
    for entry in log_data:
        if "status" in entry or "error" in entry:
            continue
        cards = entry.get("cards", [])
        if not cards:
            continue

        fname = entry["file"]
        total_cards = len(cards)
        show_cards = cards[:max_show] if max_show else cards
        omitted = total_cards - len(show_cards)

        lines.append(f"### `{fname}` ({total_cards} cartas)")
        lines.append("")
        lines.append("| ID | Nombre | Campo | Antes → Después |")
        lines.append("|--:|--------|-------|-----------------|")

        for card in show_cards:
            cid = card["id"]
            cname = card.get("name", "?")[:40]
            for change in card["changes"]:
                field = change["field"]
                before = change["before"].replace("|", "\\|").replace("\n", " ")[:35]
                after = change["after"].replace("|", "\\|").replace("\n", " ")[:35]
                lines.append(f"| {cid} | {cname} | {field} | `{before}` → `{after}` |")

        if omitted > 0:
            lines.append(f"| | *...y {omitted} cartas más* | | Ver detalle en [`MIGRATE_LOG.md`](MIGRATE_LOG.md) |")

        lines.append("")

    lines.append(f"{LOG_MARKER_END}")
    return "\n".join(lines)

def inject_log_into_readme(readme_content, log_md):
    """Inject or replace the migration log section in README."""
    if LOG_MARKER_START in readme_content and LOG_MARKER_END in readme_content:
        start_idx = readme_content.index(LOG_MARKER_START)
        end_idx = readme_content.index(LOG_MARKER_END) + len(LOG_MARKER_END)
        return readme_content[:start_idx] + log_md + readme_content[end_idx:]
    else:
        return readme_content.rstrip() + "\n\n" + log_md

def main():
    print("=" * 50)
    print("CDBtext Auto-Migrator")
    print("=" * 50)

    cache = load_cache()
    current_babel_sha = get_remote_sha("ProjectIgnis/BabelCDB", "master")
    current_ignis_sha = get_remote_sha("Team13fr/IgnisMulti", "master")

    last_babel = cache.get(BABELCDB_SHA_CACHE, "")
    last_ignis = cache.get(IGNIS_SHA_CACHE, "")

    print(f"\nBabelCDB SHA: {current_babel_sha[:7]} (último: {last_babel[:7] if last_babel else 'nunca'})")
    print(f"IgnisMulti SHA: {current_ignis_sha[:7]} (último: {last_ignis_sha[:7] if last_ignis else 'nunca'})")

    if not current_babel_sha and not current_ignis_sha:
        print("No se pudieron obtener los SHAs. Abortando.")
        return

    if last_babel and last_ignis:
        if current_babel_sha == last_babel and current_ignis_sha == last_ignis:
            print("\nNo hay cambios en los repos fuente. Nada que hacer.")
            return

    babel_dir, ignis_dir = clone_source_repos()
    en_folder = babel_dir
    es_folder = os.path.join(ignis_dir, "Español")

    if not os.path.exists(es_folder):
        print(f"ERROR: No se encontró la carpeta {es_folder}")
        return

    # Run migration (now returns log data too)
    updates, log_data = transfer_texts(en_folder, es_folder, REPO_DIR)

    # Update cache
    if current_babel_sha:
        cache[BABELCDB_SHA_CACHE] = current_babel_sha
    if current_ignis_sha:
        cache[IGNIS_SHA_CACHE] = current_ignis_sha
    save_cache(cache)

    # Copy strings.conf
    es_strings = os.path.join(es_folder, "strings.conf")
    if os.path.exists(es_strings):
        shutil.copy2(es_strings, os.path.join(REPO_DIR, "strings.conf"))

    # Generate migration log markdown (limited for README)
    log_md_readme = generate_log_markdown(log_data, cache, current_babel_sha, current_ignis_sha, limit=20)

    # Generate full log for MIGRATE_LOG.md (no limit)
    log_md_full = generate_log_markdown(log_data, cache, current_babel_sha, current_ignis_sha, limit=None)

    with open(MIGRATE_LOG_FILE, "w") as f:
        f.write(log_md_full)
    print(f"\n{MIGRATE_LOG_FILE} generado (log completo)")

    # Inject limited log into README.md
    readme_path = os.path.join(REPO_DIR, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            readme = f.read()
        new_readme = inject_log_into_readme(readme, log_md_readme)
        with open(readme_path, "w") as f:
            f.write(new_readme)
        print("README.md actualizado con log de migración (resumen)")

    if updates > 0:
        print(f"\nMigración completada: {updates} actualizaciones")
    else:
        print("\nMigración completada: sin cambios en textos")

if __name__ == "__main__":
    main()
