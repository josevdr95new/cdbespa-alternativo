#!/usr/bin/env python3
"""
CDBtext Auto-Migrator for CI/CD
Adapted from https://github.com/josevdr95new/CDBtext_migrator

Condición final:
  - Nombres en inglés (reemplazo completo)
  - Efectos (desc, str1-str7) en español, pero texto dentro de "" en inglés

El script solo migra las cartas que NO cumplen esta condición.
El log muestra: total cartas, OK, corregidas, sin traducción española (con ID y nombre).
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
    """Replace content inside double quotes of original_str with en_str's,
    preserving text outside quotes (Spanish)."""
    quoted_spans_es = re.findall(r'"(.*?)"', original_str)
    quoted_spans_en = re.findall(r'"(.*?)"', en_str)
    if len(quoted_spans_es) == len(quoted_spans_en):
        new_str = original_str
        for i in range(len(quoted_spans_en)):
            new_str = new_str.replace(f'"{quoted_spans_es[i]}"', f'"{quoted_spans_en[i]}"', 1)
        return new_str
    return original_str


def compute_target(es_data, en_data, columns):
    """Compute the target state for a card:
    - name: English (full replacement)
    - desc, str1-str7: Spanish text with English quoted content
    """
    target = {}
    for col in columns:
        if col == 'name':
            target[col] = en_data.get(col, '') or es_data.get(col, '')
        else:
            es_val = es_data.get(col, '') or ''
            en_val = en_data.get(col, '') or ''
            if es_val and en_val:
                target[col] = replace_quoted_content(es_val, en_val)
            else:
                target[col] = es_val or en_val or ''
    return target


def card_meets_condition(repo_data, en_data, columns):
    """Check if a card in the repo already meets the final condition:
    - name matches English source
    - quoted content in desc/str fields matches English source
    """
    # Check name
    repo_name = repo_data.get('name', '') or ''
    en_name = en_data.get('name', '') or ''
    if repo_name != en_name:
        return False

    # Check quoted content in desc/str fields
    for col in ['"desc"', 'str1', 'str2', 'str3', 'str4', 'str5', 'str6', 'str7']:
        repo_val = repo_data.get(col, '') or ''
        en_val = en_data.get(col, '') or ''
        repo_quoted = re.findall(r'"(.*?)"', repo_val)
        en_quoted = re.findall(r'"(.*?)"', en_val)
        if repo_quoted != en_quoted:
            return False

    return True


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
    Transfer texts from English CDBs to Spanish CDBs, but ONLY for cards
    that don't already meet the final condition in the repo.

    Returns (total_updates, log_data) where log_data contains full stats including
    list of cards missing Spanish translation (with ID and name).
    """
    en_files = {f for f in os.listdir(en_folder) if f.endswith('.cdb')}
    es_files = {f for f in os.listdir(es_folder) if f.endswith('.cdb')}
    common_files = sorted(en_files & es_files)

    os.makedirs(repo_dir, exist_ok=True)

    print(f"\nArchivos CDB comunes: {len(common_files)}")
    total_updates = 0
    all_log_data = []

    for file_name in common_files:
        en_path = os.path.join(en_folder, file_name)
        es_path = os.path.join(es_folder, file_name)
        repo_path = os.path.join(repo_dir, file_name)

        file_log = {"file": file_name, "cards": [], "missing_es": []}
        file_updates = 0

        try:
            conn_en = sqlite3.connect(en_path)
            conn_es = sqlite3.connect(es_path)
            cursor_en = conn_en.cursor()
            cursor_es = conn_es.cursor()

            columns = ['name', '"desc"', 'str1', 'str2', 'str3', 'str4', 'str5', 'str6', 'str7']

            # Get English texts
            cursor_en.execute(f'SELECT id, {", ".join(columns)} FROM texts')
            en_texts = {row[0]: {col: row[i+1] for i, col in enumerate(columns)} for row in cursor_en.fetchall()}

            # Get Spanish texts
            cursor_es.execute(f'SELECT id, {", ".join(columns)} FROM texts')
            es_texts = {row[0]: {col: row[i+1] for i, col in enumerate(columns)} for row in cursor_es.fetchall()}

            # Counters
            total_en = len(en_texts)
            total_es = len(es_texts)
            total_ok = 0
            total_fixed = 0
            total_no_es = 0

            # If repo CDB doesn't exist yet, create it from Spanish base
            if not os.path.exists(repo_path):
                shutil.copy2(es_path, repo_path)
                print(f"  {file_name}: creado desde base española")

            conn_repo = sqlite3.connect(repo_path)
            cursor_repo = conn_repo.cursor()

            # Get current repo texts
            cursor_repo.execute(f'SELECT id, {", ".join(columns)} FROM texts')
            repo_texts = {row[0]: {col: row[i+1] for i, col in enumerate(columns)} for row in cursor_repo.fetchall()}

            # Process cards that exist in both English and Spanish sources
            for text_id, en_data in en_texts.items():
                if text_id not in es_texts:
                    # Card exists in EN but NOT in ES — no Spanish translation yet
                    total_no_es += 1
                    file_log["missing_es"].append({
                        "id": text_id,
                        "name": en_data.get('name', '') or '(sin nombre)'
                    })
                    continue

                es_data = es_texts[text_id]

                # Compute target state (what the card SHOULD look like)
                target_data = compute_target(es_data, en_data, columns)

                if text_id in repo_texts:
                    # Card exists in repo — check if it already meets the condition
                    repo_data = repo_texts[text_id]

                    if card_meets_condition(repo_data, en_data, columns):
                        # Card already correct — skip entirely
                        total_ok += 1
                        continue

                    # Card doesn't meet condition — find what needs to change
                    updates = {}
                    card_changes = []

                    for col in columns:
                        repo_val = repo_data.get(col, '') or ''
                        target_val = target_data.get(col, '') or ''

                        if repo_val != target_val:
                            updates[col] = target_val
                            card_changes.append({
                                "field": col.strip('"') if col == '"desc"' else col,
                                "before": repo_val[:80],
                                "after": target_val[:80]
                            })

                    if updates:
                        set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
                        params = list(updates.values()) + [text_id]
                        cursor_repo.execute(f"UPDATE texts SET {set_clause} WHERE id = ?", params)
                        file_updates += 1
                        total_fixed += 1
                        file_log["cards"].append({
                            "id": text_id,
                            "name": target_data.get('name', '?'),
                            "changes": card_changes
                        })
                else:
                    # New card not in repo — insert with target values
                    cursor_repo.execute(
                        f'INSERT INTO texts (id, {", ".join(columns)}) VALUES (?, {", ".join(["?"] * len(columns))})',
                        [text_id] + [target_data.get(col, '') for col in columns]
                    )
                    file_updates += 1
                    total_fixed += 1
                    card_changes = []
                    for col in columns:
                        target_val = target_data.get(col, '') or ''
                        if target_val:
                            card_changes.append({
                                "field": col.strip('"') if col == '"desc"' else col,
                                "before": "(nueva)",
                                "after": target_val[:80]
                            })
                    file_log["cards"].append({
                        "id": text_id,
                        "name": target_data.get('name', '?'),
                        "changes": card_changes,
                        "new_card": True
                    })

            # Also add Spanish-only cards that aren't in the repo yet
            total_no_en = 0
            for text_id, es_data in es_texts.items():
                if text_id not in en_texts:
                    total_no_en += 1
                    if text_id not in repo_texts:
                        # Spanish-only card — add as-is
                        cursor_repo.execute(
                            f'INSERT INTO texts (id, {", ".join(columns)}) VALUES (?, {", ".join(["?"] * len(columns))})',
                            [text_id] + [es_data.get(col, '') or '' for col in columns]
                        )
                        file_updates += 1
                        file_log["cards"].append({
                            "id": text_id,
                            "name": es_data.get('name', '(solo español)'),
                            "changes": [{"field": "new", "before": "(nueva)", "after": "carta solo español"}],
                            "new_card": True
                        })

            conn_repo.commit()
            conn_repo.close()

            # Store stats
            file_log["stats"] = {
                "total_en": total_en,
                "total_es": total_es,
                "total_ok": total_ok,
                "total_fixed": total_fixed,
                "total_no_es": total_no_es,
                "total_no_en": total_no_en
            }

        except Exception as e:
            print(f"  ERROR en {file_name}: {e}")
            file_log["error"] = str(e)
            try:
                if 'conn_repo' in locals():
                    conn_repo.rollback()
                    conn_repo.close()
            except:
                pass
        finally:
            conn_en.close()
            conn_es.close()

        total_updates += file_updates
        file_log["updated_count"] = file_updates
        all_log_data.append(file_log)

        stats = file_log.get("stats", {})
        print(f"  {file_name}: EN={stats.get('total_en',0)} ES={stats.get('total_es',0)} OK={stats.get('total_ok',0)} corregidas={file_updates} sin_trad_es={stats.get('total_no_es',0)}")

    # Handle Spanish-only files (files that exist in Spanish but not English source)
    es_only = sorted(es_files - en_files)
    for file_name in es_only:
        src = os.path.join(es_folder, file_name)
        dst = os.path.join(repo_dir, file_name)
        needs_copy = not os.path.exists(dst)
        if not needs_copy:
            needs_copy = os.path.getmtime(src) > os.path.getmtime(dst)
        if needs_copy:
            shutil.copy2(src, dst)
            all_log_data.append({"file": file_name, "status": "solo español, actualizado"})
            print(f"  {file_name}: actualizado (solo español)")
        else:
            all_log_data.append({"file": file_name, "status": "solo español, sin cambios"})

    # Handle English-only files (files that exist in English but not Spanish source)
    en_only = sorted(en_files - es_files)
    for file_name in en_only:
        src = os.path.join(en_folder, file_name)
        dst = os.path.join(repo_dir, file_name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            all_log_data.append({"file": file_name, "status": "solo inglés, copiado"})
            print(f"  {file_name}: copiado (solo inglés)")

    # Grand totals
    grand_total_en = sum(e.get("stats", {}).get("total_en", 0) for e in all_log_data if "stats" in e)
    grand_total_es = sum(e.get("stats", {}).get("total_es", 0) for e in all_log_data if "stats" in e)
    grand_total_ok = sum(e.get("stats", {}).get("total_ok", 0) for e in all_log_data if "stats" in e)
    grand_total_fixed = total_updates
    grand_total_no_es = sum(e.get("stats", {}).get("total_no_es", 0) for e in all_log_data if "stats" in e)
    grand_total_no_en = sum(e.get("stats", {}).get("total_no_en", 0) for e in all_log_data if "stats" in e)

    print(f"\nTotal general:")
    print(f"  Cartas EN: {grand_total_en}")
    print(f"  Cartas ES: {grand_total_es}")
    print(f"  OK (ya cumplen): {grand_total_ok}")
    print(f"  Corregidas: {grand_total_fixed}")
    print(f"  Sin traducción ES: {grand_total_no_es}")
    print(f"  Solo en ES: {grand_total_no_en}")

    return total_updates, all_log_data


def generate_log_markdown(log_data, cache, babel_sha, ignis_sha, limit=None, missing_limit=None):
    """Generate a markdown migration log with full stats and missing translation list."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"{LOG_MARKER_START}",
        f"## 🔄 Log de migración",
        f"",
        f"<sub>Última verificación: **{now}**</sub>",
        f"",
        f"**Condición:** nombres en inglés · efectos en español · texto en `\"\"` en inglés",
        f"",
        f"**Fuentes:**",
        f"- `ProjectIgnis/BabelCDB` @ `{babel_sha[:7]}`",
        f"- `Team13fr/IgnisMulti` @ `{ignis_sha[:7]}`",
        f"",
    ]

    # Summary table with full stats
    lines.append("### Estado por archivo")
    lines.append("")
    lines.append("| Archivo | Cartas EN | Traducidas ES | ✅ OK | 🔧 Corregidas | ❌ Sin trad. ES |")
    lines.append("|---------|----------:|--------------:|------:|--------------:|----------------:|")

    grand_total_en = 0
    grand_total_es_common = 0
    grand_total_ok = 0
    grand_total_fixed = 0
    grand_total_no_es = 0

    for entry in log_data:
        fname = entry["file"]
        if "error" in entry:
            lines.append(f"| `{fname}` | — | — | — | — | ❌ Error |")
            continue
        if "status" in entry:
            lines.append(f"| `{fname}` | — | — | — | — | 📋 {entry['status']} |")
            continue

        stats = entry.get("stats", {})
        t_en = stats.get("total_en", 0)
        t_ok = stats.get("total_ok", 0)
        t_fixed = entry.get("updated_count", 0)
        t_no_es = stats.get("total_no_es", 0)
        t_es_common = t_en - t_no_es

        grand_total_en += t_en
        grand_total_es_common += t_es_common
        grand_total_ok += t_ok
        grand_total_fixed += t_fixed
        grand_total_no_es += t_no_es

        fixed_str = f"**{t_fixed}**" if t_fixed > 0 else "0"
        no_es_str = f"**{t_no_es}**" if t_no_es > 0 else "0"

        lines.append(f"| `{fname}` | {t_en} | {t_es_common} | {t_ok} | {fixed_str} | {no_es_str} |")

    lines.append(f"| **Total** | **{grand_total_en}** | **{grand_total_es_common}** | **{grand_total_ok}** | **{grand_total_fixed}** | **{grand_total_no_es}** |")
    lines.append("")

    # Explanation
    lines.append("<sub>**Cartas EN** = total en BabelCDB · **Traducidas ES** = también en IgnisMulti/Español · **✅ OK** = ya cumplen condición · **🔧 Corregidas** = aplicadas esta ejecución · **❌ Sin trad. ES** = no existen en la DB española aún</sub>")
    lines.append("")

    if grand_total_fixed == 0 and grand_total_no_es == 0:
        lines.append("*Todas las cartas traducidas ya cumplen la condición. No se requirió migración.*")
        lines.append("")
    elif grand_total_fixed == 0:
        lines.append("*Todas las cartas traducidas ya cumplen la condición.*")
        lines.append("")

    # Section: Cartas corregidas (only for files with fixes)
    max_show = limit
    has_fixes = any(e.get("cards") for e in log_data if "status" not in e and "error" not in e)
    if has_fixes:
        lines.append("### 🔧 Cartas corregidas")
        lines.append("")
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

            lines.append(f"**`{fname}`** ({total_cards} cartas)")
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

    # Section: Cartas sin traducción española
    max_missing = missing_limit
    has_missing = any(e.get("missing_es") for e in log_data if "status" not in e and "error" not in e)
    if has_missing:
        lines.append("### ❌ Cartas sin traducción española")
        lines.append("")
        lines.append("Estas cartas existen en BabelCDB (inglés) pero no en IgnisMulti/Español. Se incluirán automáticamente cuando se traduzcan.")
        lines.append("")

        for entry in log_data:
            if "status" in entry or "error" in entry:
                continue
            missing = entry.get("missing_es", [])
            if not missing:
                continue

            fname = entry["file"]
            total_missing = len(missing)
            show_missing = missing[:max_missing] if max_missing else missing
            omitted = total_missing - len(show_missing)

            lines.append(f"**`{fname}`** ({total_missing} cartas)")
            lines.append("")
            lines.append("| ID | Nombre (EN) |")
            lines.append("|--:|-------------|")

            for card in show_missing:
                cid = card["id"]
                cname = card.get("name", "?").replace("|", "\\|")[:50]
                lines.append(f"| {cid} | {cname} |")

            if omitted > 0:
                lines.append(f"| | *...y {omitted} cartas más* |")

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
    print("Condición: nombres EN, efectos ES, \"\" EN")
    print("=" * 50)

    cache = load_cache()
    current_babel_sha = get_remote_sha("ProjectIgnis/BabelCDB", "master")
    current_ignis_sha = get_remote_sha("Team13fr/IgnisMulti", "master")

    last_babel = cache.get(BABELCDB_SHA_CACHE, "")
    last_ignis = cache.get(IGNIS_SHA_CACHE, "")

    print(f"\nBabelCDB SHA: {current_babel_sha[:7]} (último: {last_babel[:7] if last_babel else 'nunca'})")
    print(f"IgnisMulti SHA: {current_ignis_sha[:7]} (último: {last_ignis[:7] if last_ignis else 'nunca'})")

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

    # Run migration — only fixes cards that don't meet the condition
    updates, log_data = transfer_texts(en_folder, es_folder, REPO_DIR)

    # Update cache
    if current_babel_sha:
        cache[BABELCDB_SHA_CACHE] = current_babel_sha
    if current_ignis_sha:
        cache[IGNIS_SHA_CACHE] = current_ignis_sha
    save_cache(cache)

    # Copy strings.conf if updated
    es_strings = os.path.join(es_folder, "strings.conf")
    if os.path.exists(es_strings):
        repo_strings = os.path.join(REPO_DIR, "strings.conf")
        needs_copy = not os.path.exists(repo_strings)
        if not needs_copy:
            needs_copy = os.path.getmtime(es_strings) > os.path.getmtime(repo_strings)
        if needs_copy:
            shutil.copy2(es_strings, repo_strings)

    # Generate migration log markdown (limited for README: 20 fixes, 50 missing)
    log_md_readme = generate_log_markdown(log_data, cache, current_babel_sha, current_ignis_sha, limit=20, missing_limit=50)

    # Generate full log for MIGRATE_LOG.md (no limits)
    log_md_full = generate_log_markdown(log_data, cache, current_babel_sha, current_ignis_sha, limit=None, missing_limit=None)

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
        print(f"\nMigración completada: {updates} cartas corregidas")
    else:
        print("\nMigración completada: todas las cartas traducidas ya cumplen la condición")


if __name__ == "__main__":
    main()
