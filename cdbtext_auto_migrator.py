#!/usr/bin/env python3
"""
CDBtext Auto-Migrator for CI/CD
Adapted from https://github.com/josevdr95new/CDBtext_migrator

Transforma las cartas españolas con la condición:
  - Nombres en inglés (desde BabelCDB)
  - Efectos en español, pero texto dentro de "" en inglés

No "corrige" nada — aplica la transformación directamente.
Si una carta ya está OK en el repo, la salta.
Si una carta no existe en la DB española, no se migra (se lista como pendiente).
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


def transform_card(es_data, en_data, columns):
    """Apply the final transformation:
    - name: English (full replacement from BabelCDB)
    - desc, str1-str7: Spanish text with English quoted content
    """
    result = {}
    for col in columns:
        if col == 'name':
            result[col] = en_data.get(col, '') or es_data.get(col, '')
        else:
            es_val = es_data.get(col, '') or ''
            en_val = en_data.get(col, '') or ''
            if es_val and en_val:
                result[col] = replace_quoted_content(es_val, en_val)
            else:
                result[col] = es_val or en_val or ''
    return result


def card_is_ok(repo_data, en_data, columns):
    """Check if a card in the repo already matches the transformed state."""
    repo_name = repo_data.get('name', '') or ''
    en_name = en_data.get('name', '') or ''
    if repo_name != en_name:
        return False
    for col in ['"desc"', 'str1', 'str2', 'str3', 'str4', 'str5', 'str6', 'str7']:
        repo_val = repo_data.get(col, '') or ''
        en_val = en_data.get(col, '') or ''
        if re.findall(r'"(.*?)"', repo_val) != re.findall(r'"(.*?)"', en_val):
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
    Build the repo CDBs from scratch:
    1. Copy Spanish CDB as base
    2. For each card in both EN and ES: transform (name EN, "" EN) and write to repo
    3. Cards only in EN = no Spanish translation yet (listed as missing)
    
    Returns (total_new, log_data)
    """
    en_files = {f for f in os.listdir(en_folder) if f.endswith('.cdb')}
    es_files = {f for f in os.listdir(es_folder) if f.endswith('.cdb')}
    common_files = sorted(en_files & es_files)

    os.makedirs(repo_dir, exist_ok=True)

    print(f"\nArchivos CDB comunes: {len(common_files)}")
    total_new = 0
    all_log_data = []

    for file_name in common_files:
        en_path = os.path.join(en_folder, file_name)
        es_path = os.path.join(es_folder, file_name)
        repo_path = os.path.join(repo_dir, file_name)

        file_log = {"file": file_name, "new_cards": [], "missing_es": []}

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

            # Stats
            total_en = len(en_texts)
            total_es = len(es_texts)
            total_ok = 0
            total_translated = 0  # cards that exist in both EN and ES (can be translated)
            total_new_cards = 0
            total_no_es = 0

            # Copy Spanish CDB as base for the repo
            shutil.copy2(es_path, repo_path)

            conn_repo = sqlite3.connect(repo_path)
            cursor_repo = conn_repo.cursor()

            # Apply transformation to all cards that exist in both EN and ES
            for text_id, en_data in en_texts.items():
                if text_id not in es_texts:
                    # Card not in Spanish DB — can't translate
                    total_no_es += 1
                    file_log["missing_es"].append({
                        "id": text_id,
                        "name": en_data.get('name', '') or '(sin nombre)'
                    })
                    continue

                total_translated += 1
                es_data = es_texts[text_id]
                transformed = transform_card(es_data, en_data, columns)

                # Check if repo already has this card correctly
                cursor_repo.execute(f'SELECT {", ".join(columns)} FROM texts WHERE id = ?', (text_id,))
                repo_row = cursor_repo.fetchone()

                if repo_row:
                    repo_data = {col: val for col, val in zip(columns, repo_row)}
                    if card_is_ok(repo_data, en_data, columns):
                        total_ok += 1
                        continue

                    # Update with transformed values
                    set_clause = ", ".join([f"{col} = ?" for col in columns])
                    params = [transformed.get(col, '') for col in columns] + [text_id]
                    cursor_repo.execute(f"UPDATE texts SET {set_clause} WHERE id = ?", params)
                    total_new_cards += 1
                    file_log["new_cards"].append({
                        "id": text_id,
                        "name": transformed.get('name', '?')
                    })
                else:
                    # Insert new card
                    cursor_repo.execute(
                        f'INSERT INTO texts (id, {", ".join(columns)}) VALUES (?, {", ".join(["?"] * len(columns))})',
                        [text_id] + [transformed.get(col, '') for col in columns]
                    )
                    total_new_cards += 1
                    file_log["new_cards"].append({
                        "id": text_id,
                        "name": transformed.get('name', '?')
                    })

            conn_repo.commit()
            conn_repo.close()

            file_log["stats"] = {
                "total_en": total_en,
                "total_es": total_es,
                "total_translated": total_translated,
                "total_ok": total_ok,
                "total_new": total_new_cards,
                "total_no_es": total_no_es
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

        total_new += total_new_cards
        all_log_data.append(file_log)

        stats = file_log.get("stats", {})
        print(f"  {file_name}: EN={stats.get('total_en',0)} traducibles={stats.get('total_translated',0)} OK={stats.get('total_ok',0)} nuevas={stats.get('total_new',0)} sin_ES={stats.get('total_no_es',0)}")

    # Spanish-only files (no matching EN CDB)
    es_only = sorted(es_files - en_files)
    for file_name in es_only:
        src = os.path.join(es_folder, file_name)
        dst = os.path.join(repo_dir, file_name)
        needs_copy = not os.path.exists(dst)
        if not needs_copy:
            needs_copy = os.path.getmtime(src) > os.path.getmtime(dst)
        if needs_copy:
            shutil.copy2(src, dst)
            all_log_data.append({"file": file_name, "status": "solo español, copiado"})
            print(f"  {file_name}: copiado (solo español)")

    # English-only files (no matching ES CDB)
    en_only = sorted(en_files - es_files)
    for file_name in en_only:
        src = os.path.join(en_folder, file_name)
        dst = os.path.join(repo_dir, file_name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            all_log_data.append({"file": file_name, "status": "solo inglés, copiado"})
            print(f"  {file_name}: copiado (solo inglés)")

    return total_new, all_log_data


def generate_log_markdown(log_data, cache, babel_sha, ignis_sha, limit=None, missing_limit=None):
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

    # Summary table
    lines.append("### Estado por archivo")
    lines.append("")
    lines.append("| Archivo | EN | Traducidas | ✅ OK | 🆕 Nuevas | ❌ Sin trad. ES |")
    lines.append("|---------|---:|-----------:|------:|----------:|---------------:|")

    g_en = g_trans = g_ok = g_new = g_no_es = 0

    for entry in log_data:
        fname = entry["file"]
        if "error" in entry:
            lines.append(f"| `{fname}` | — | — | — | — | ❌ Error |")
            continue
        if "status" in entry:
            lines.append(f"| `{fname}` | — | — | — | — | 📋 {entry['status']} |")
            continue

        s = entry.get("stats", {})
        t_en = s.get("total_en", 0)
        t_trans = s.get("total_translated", 0)
        t_ok = s.get("total_ok", 0)
        t_new = s.get("total_new", 0)
        t_no_es = s.get("total_no_es", 0)

        g_en += t_en
        g_trans += t_trans
        g_ok += t_ok
        g_new += t_new
        g_no_es += t_no_es

        new_str = f"**{t_new}**" if t_new > 0 else "0"
        no_es_str = f"**{t_no_es}**" if t_no_es > 0 else "0"

        lines.append(f"| `{fname}` | {t_en} | {t_trans} | {t_ok} | {new_str} | {no_es_str} |")

    lines.append(f"| **Total** | **{g_en}** | **{g_trans}** | **{g_ok}** | **{g_new}** | **{g_no_es}** |")
    lines.append("")
    lines.append("<sub>**EN** = total BabelCDB · **Traducidas** = también en IgnisMulti/ES · **✅ OK** = ya transformadas · **🆕 Nuevas** = transformadas esta ejecución · **❌ Sin trad. ES** = no existen en DB española</sub>")
    lines.append("")

    if g_new == 0:
        lines.append("*Todas las cartas disponibles ya están transformadas. No hay cartas nuevas.*")
        lines.append("")

    # New cards (only show if there are any)
    max_show = limit
    if g_new > 0:
        lines.append("### 🆕 Cartas transformadas")
        lines.append("")
        for entry in log_data:
            if "status" in entry or "error" in entry:
                continue
            new_cards = entry.get("new_cards", [])
            if not new_cards:
                continue
            fname = entry["file"]
            total = len(new_cards)
            show = new_cards[:max_show] if max_show else new_cards
            omitted = total - len(show)
            lines.append(f"**`{fname}`** ({total} cartas)")
            lines.append("")
            lines.append("| ID | Nombre |")
            lines.append("|--:|--------|")
            for card in show:
                cname = card.get("name", "?").replace("|", "\\|")[:50]
                lines.append(f"| {card['id']} | {cname} |")
            if omitted > 0:
                lines.append(f"| | *...y {omitted} más* |")
            lines.append("")

    # Missing Spanish translations
    max_missing = missing_limit
    if g_no_es > 0:
        lines.append("### ❌ Cartas sin traducción española")
        lines.append("")
        lines.append("Estas cartas existen en BabelCDB pero no en IgnisMulti/Español. Se transformarán automáticamente cuando haya traducción disponible.")
        lines.append("")

        for entry in log_data:
            if "status" in entry or "error" in entry:
                continue
            missing = entry.get("missing_es", [])
            if not missing:
                continue
            fname = entry["file"]
            total = len(missing)
            show = missing[:max_missing] if max_missing else missing
            omitted = total - len(show)
            lines.append(f"**`{fname}`** ({total} cartas)")
            lines.append("")
            lines.append("| ID | Nombre (EN) |")
            lines.append("|--:|-------------|")
            for card in show:
                cname = card.get("name", "?").replace("|", "\\|")[:50]
                lines.append(f"| {card['id']} | {cname} |")
            if omitted > 0:
                lines.append(f"| | *...y {omitted} más* |")
            lines.append("")

    lines.append(f"{LOG_MARKER_END}")
    return "\n".join(lines)


def inject_log_into_readme(readme_content, log_md):
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

    new_cards, log_data = transfer_texts(en_folder, es_folder, REPO_DIR)

    # Update cache
    if current_babel_sha:
        cache[BABELCDB_SHA_CACHE] = current_babel_sha
    if current_ignis_sha:
        cache[IGNIS_SHA_CACHE] = current_ignis_sha
    save_cache(cache)

    # Copy strings.conf if needed
    es_strings = os.path.join(es_folder, "strings.conf")
    if os.path.exists(es_strings):
        repo_strings = os.path.join(REPO_DIR, "strings.conf")
        needs_copy = not os.path.exists(repo_strings)
        if not needs_copy:
            needs_copy = os.path.getmtime(es_strings) > os.path.getmtime(repo_strings)
        if needs_copy:
            shutil.copy2(es_strings, repo_strings)

    # Generate logs
    log_md_readme = generate_log_markdown(log_data, cache, current_babel_sha, current_ignis_sha, limit=50, missing_limit=50)
    log_md_full = generate_log_markdown(log_data, cache, current_babel_sha, current_ignis_sha, limit=None, missing_limit=None)

    with open(MIGRATE_LOG_FILE, "w") as f:
        f.write(log_md_full)
    print(f"\n{MIGRATE_LOG_FILE} generado")

    readme_path = os.path.join(REPO_DIR, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            readme = f.read()
        new_readme = inject_log_into_readme(readme, log_md_readme)
        with open(readme_path, "w") as f:
            f.write(new_readme)
        print("README.md actualizado")

    if new_cards > 0:
        print(f"\nCompletado: {new_cards} cartas nuevas transformadas")
    else:
        print("\nCompletado: todas las cartas disponibles ya están transformadas")


if __name__ == "__main__":
    main()
