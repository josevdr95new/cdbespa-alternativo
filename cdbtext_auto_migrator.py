#!/usr/bin/env python3
"""
CDBtext Auto-Migrator for CI/CD
Adapted from https://github.com/josevdr95new/CDBtext_migrator

- Clones BabelCDB (en) and IgnisMulti/Español (es)
- Transfers text fields from English CDBs into the Spanish copies
- Writes updated CDBs directly into the repo
- Tracks last processed SHAs to avoid unnecessary work
"""

import sqlite3
import os
import re
import json
import shutil
import subprocess
from datetime import datetime

REPO_DIR = os.environ.get("REPO_DIR", ".")
CACHE_FILE = os.path.join(REPO_DIR, ".migrate_cache.json")
BABELCDB_SHA_CACHE = "last_babelcdb_sha"
IGNIS_SHA_CACHE = "last_ignis_sha"

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

    # Clean previous runs
    for d in [babel_dir, ignis_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)

    # Clone BabelCDB (English base)
    babel_url = f"https://{token}@github.com/ProjectIgnis/BabelCDB.git" if token else "https://github.com/ProjectIgnis/BabelCDB.git"
    print("Cloning BabelCDB (English)...")
    subprocess.run(["git", "clone", "--depth", "1", babel_url, babel_dir], check=True, capture_output=True)

    # Clone IgnisMulti (Spanish translations)
    ignis_url = f"https://{token}@github.com/Team13fr/IgnisMulti.git" if token else "https://github.com/Team13fr/IgnisMulti.git"
    print("Cloning IgnisMulti (Spanish)...")
    subprocess.run(["git", "clone", "--depth", "1", ignis_url, ignis_dir], check=True, capture_output=True)

    return babel_dir, ignis_dir

def transfer_texts(en_folder, es_folder, repo_dir):
    """Transfer texts from English CDBs to Spanish CDBs, writing results to repo_dir."""
    en_files = {f for f in os.listdir(en_folder) if f.endswith('.cdb')}
    es_files = {f for f in os.listdir(es_folder) if f.endswith('.cdb')}
    common_files = sorted(en_files & es_files)

    print(f"\nCommon CDB files: {len(common_files)}")
    total_updates = 0

    for file_name in common_files:
        en_path = os.path.join(en_folder, file_name)
        es_path = os.path.join(es_folder, file_name)
        repo_path = os.path.join(repo_dir, file_name)

        # Copy the Spanish version to the repo (overwrite existing)
        shutil.copy2(es_path, repo_path)

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

                    for col in columns:
                        es_val = es_data[col]
                        en_val = en_data.get(col)

                        if col in ['"desc"', 'str1', 'str2', 'str3', 'str4', 'str5', 'str6', 'str7']:
                            if es_val and en_val:
                                new_val = replace_quoted_content(es_val, en_val)
                                if new_val != es_val:
                                    updates[col] = new_val
                        else:  # 'name' — full replacement
                            if en_val and en_val != es_data.get('name', ''):
                                updates[col] = en_val

                    if updates:
                        set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
                        params = list(updates.values()) + [text_id]
                        cursor_repo.execute(f"UPDATE texts SET {set_clause} WHERE id = ?", params)
                        file_updates += 1

            conn_repo.commit()
            total_updates += file_updates
            print(f"  {file_name}: {file_updates} registros actualizados")

        except Exception as e:
            print(f"  ERROR en {file_name}: {e}")
            if conn_repo:
                conn_repo.rollback()
        finally:
            conn_en.close()
            conn_repo.close()

    # Also copy files that exist in Spanish but not in English (prerelease, etc.)
    es_only = sorted(es_files - en_files)
    for file_name in es_only:
        src = os.path.join(es_folder, file_name)
        dst = os.path.join(repo_dir, file_name)
        shutil.copy2(src, dst)
        print(f"  {file_name}: copiado (solo español, sin migración)")

    # Also copy prerelease/release files from English that may not be in Spanish
    en_only = sorted(en_files - es_files)
    for file_name in en_only:
        src = os.path.join(en_folder, file_name)
        dst = os.path.join(repo_dir, file_name)
        shutil.copy2(src, dst)
        print(f"  {file_name}: copiado (solo inglés, sin traducción)")

    print(f"\nTotal: {total_updates} registros actualizados en {len(common_files)} archivos")
    return total_updates

def main():
    print("=" * 50)
    print("CDBtext Auto-Migrator")
    print("=" * 50)

    # Check if sources have changed
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

    # Always run on first time; skip only if both SHAs match
    if last_babel and last_ignis:
        if current_babel_sha == last_babel and current_ignis_sha == last_ignis:
            print("\nNo hay cambios en los repos fuente. Nada que hacer.")
            return

    # Clone source repos
    babel_dir, ignis_dir = clone_source_repos()
    en_folder = babel_dir  # BabelCDB CDBs are at root
    es_folder = os.path.join(ignis_dir, "Español")  # Spanish is in Español/ subfolder

    if not os.path.exists(es_folder):
        print(f"ERROR: No se encontró la carpeta {es_folder}")
        return

    # Run migration
    updates = transfer_texts(en_folder, es_folder, REPO_DIR)

    # Update cache
    if current_babel_sha:
        cache[BABELCDB_SHA_CACHE] = current_babel_sha
    if current_ignis_sha:
        cache[IGNIS_SHA_CACHE] = current_ignis_sha
    save_cache(cache)

    # Copy strings.conf from Spanish if it exists
    es_strings = os.path.join(es_folder, "strings.conf")
    if os.path.exists(es_strings):
        shutil.copy2(es_strings, os.path.join(REPO_DIR, "strings.conf"))
        print("strings.conf copiado")

    if updates > 0:
        print(f"\nMigración completada: {updates} actualizaciones")
    else:
        print("\nMigración completada: sin cambios en textos")

if __name__ == "__main__":
    main()
