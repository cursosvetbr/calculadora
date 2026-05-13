"""
Script to enrich an EAD export JSON with professor names fetched from the EAD Plataforma API.

Usage:
    python add_professor_names.py --file ead_export.json --base-url https://example.com --token TOKEN

Behavior:
 - The script walks the JSON structure recursively and, for every dict that contains a
   `professor_id` key (and does not already have `professor_name`), it will request
   the user data from the EAD API and add `professor_name` to that dict.
 - The script makes a backup copy of the original JSON before overwriting it.

Notes:
 - Provide `--base-url` and `--token` (or set TOKEN_EAD in the .env file) for the API.
 - The script uses a conservative retry strategy and looks for likely name fields in the
   API response ("name", "full_name", "nome"). Adjust if your API returns different keys.
"""
import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import urllib.request
import urllib.error
import shutil


DEFAULT_FILE = "ead_export.json"


def load_token_from_env_or_dotenv() -> str:
    # Prefer environment variable
    token = os.environ.get("TOKEN_EAD")
    if token:
        return token
    # Try simple .env parsing in current folder
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with env_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() == "TOKEN_EAD":
                        return v.strip()
    return ""


def get_user_name(base_url: str, token: str | None, user_id: Any, timeout=10, max_retries=3) -> str:
    """Request the EAD Plataforma for the user and return a name string.

    The function expects endpoint GET {base_url.rstrip('/')}/users/{user_id}
    and that the response is JSON containing a name field (name/full_name/nome).
    """
    if not user_id:
        return ""
    url = f"{base_url.rstrip('/')}/users/{user_id}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    attempt = 0
    while attempt < max_retries:
        attempt += 1
        try:
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
                # Try several possible fields
                for key in ("name", "full_name", "nome", "username"):
                    if isinstance(data, dict) and key in data and data[key]:
                        return str(data[key])
                # If the user object is nested
                if isinstance(data, dict):
                    # Try common nested shapes
                    for candidate in ("data", "user", "usuario"):
                        sub = data.get(candidate)
                        if isinstance(sub, dict):
                            for key in ("name", "full_name", "nome", "username"):
                                if key in sub and sub[key]:
                                    return str(sub[key])
                # Last resort: stringify the whole response
                return json.dumps(data)
        except urllib.error.HTTPError as e:
            # 404 -> no user, return empty
            if e.code == 404:
                return ""
            # For server errors, retry
            if 500 <= e.code < 600 and attempt < max_retries:
                time.sleep(1 + attempt)
                continue
            # Unexpected HTTP error; break and return empty
            return ""
        except Exception:
            # network error, retry
            if attempt < max_retries:
                time.sleep(1 + attempt)
                continue
            return ""


def find_and_update(obj: Any, base_url: str, token: str, stats: Dict[str, int]):
    """Recursively walk obj and update dicts containing 'professor_id'.

    stats is a dict used to accumulate counters (checked, updated, skipped).
    """
    if isinstance(obj, dict):
        stats["checked"] += 1
        if "professor_id" in obj:
            pid = obj.get("professor_id")
            # Skip if already present
            if obj.get("professor_name"):
                stats["skipped_existing"] += 1
            else:
                stats["to_update"] += 1
                name = get_user_name(base_url, token, pid)
                if name:
                    obj["professor_name"] = name
                    stats["updated"] += 1
                else:
                    stats["not_found"] += 1
        # Recurse into values
        for v in obj.values():
            find_and_update(v, base_url, token, stats)
    elif isinstance(obj, list):
        for item in obj:
            find_and_update(item, base_url, token, stats)


def backup_file(path: Path) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    dest = path.with_suffix(path.suffix + f".bak.{ts}")
    path.replace(dest)
    return dest


def main():
    parser = argparse.ArgumentParser(description="Add professor names to an EAD export JSON.")
    parser.add_argument("--file", "-f", default=DEFAULT_FILE, help="path to ead_export.json")
    parser.add_argument("--base-url", "-b", required=True, help="EAD Plataforma base URL (e.g. https://api.eadplataforma.com)")
    parser.add_argument("--token", "-t", default=None, help="API token (or set TOKEN_EAD in env/.env)")
    args = parser.parse_args()

    token = args.token or load_token_from_env_or_dotenv()
    if not token:
        print("ERROR: no token provided. Pass --token or set TOKEN_EAD in environment/.env")
        return

    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        return

    print(f"Loading JSON from {path}...")
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except MemoryError:
        print("File too large to load into memory. Consider using a streaming tool (ijson) or split the file.")
        return
    except Exception as e:
        print(f"Failed to load JSON: {e}")
        return

    stats = {"checked": 0, "to_update": 0, "updated": 0, "skipped_existing": 0, "not_found": 0}
    find_and_update(data, args.base_url, token, stats)

    print("Summary:")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    # Backup original file
    backup_path = path.with_suffix(path.suffix + ".bak")
    # If backup exists, make timestamped backup
    if path.exists():
        # copy original to backup (do not move to avoid losing original on failure)
        import shutil

        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        backup_path = path.with_suffix(path.suffix + f".bak.{ts}")
        shutil.copy2(path, backup_path)
        print(f"Backup saved to {backup_path}")

    # Write the updated JSON (pretty printed)
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Updated file written to {path}")
    except Exception as e:
        print(f"Failed to write updated JSON: {e}")
        # try to restore backup
        try:
            shutil.copy2(backup_path, path)
            print("Original file restored from backup.")
        except Exception:
            print("Failed to restore original file; manual recovery may be required.")


if __name__ == "__main__":
    main()



