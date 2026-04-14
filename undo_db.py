"""
undo_db.py — Kivotos Halo Asset Tool
Undo / restore-point database.

Workflow
--------
  add_entry()   → hash files → compress → write DB entry
  restore_entry() → decompress to temp → copy back to original paths
  remove_entry()  → delete archive + DB row

DB location : ~/KivotosToolOutput/undo_db/database.json
Archives    : ~/KivotosToolOutput/undo_db/archives/
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import tarfile
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────

_HOME         = Path.home()
DB_ROOT       = _HOME / "G.E.M.A.T.R.I.A_Output" / "undo_db"
DB_FILE       = DB_ROOT / "database.json"
ARCHIVES_DIR  = DB_ROOT / "archives"

SUPPORTED_FORMATS = ["tar.gz", "tar.zstd", "7z"]
FORMAT_EXTS = {
    "tar.gz":   ".tar.gz",
    "tar.zstd": ".tar.zst",
    "7z":       ".7z",
}

# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_dirs() -> None:
    DB_ROOT.mkdir(parents=True, exist_ok=True)
    ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)


def _log(cb, msg: str) -> None:
    if cb:
        cb(msg)


def fmt_size(n: int) -> str:
    if n < 1_024:
        return f"{n} B"
    if n < 1_048_576:
        return f"{n / 1_024:.1f} KB"
    return f"{n / 1_048_576:.2f} MB"


# ─────────────────────────────────────────────────────────────────────────────
# DB I/O
# ─────────────────────────────────────────────────────────────────────────────

def load_db() -> dict:
    """Load the JSON database, creating it if absent."""
    _ensure_dirs()
    if DB_FILE.exists():
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"version": "1.0", "entries": []}


def save_db(db: dict) -> None:
    _ensure_dirs()
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


def list_entries() -> list[dict]:
    """Return all DB entries, newest first."""
    return load_db().get("entries", [])


# ─────────────────────────────────────────────────────────────────────────────
# Hashing
# ─────────────────────────────────────────────────────────────────────────────

def hash_file(path: str) -> str:
    """SHA-256 of a single file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65_536), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_paths(paths: list[str], log_cb=None) -> dict[str, str]:
    """
    Recursively hash all files under the given paths.
    Returns {absolute_path: sha256}.
    """
    result: dict[str, str] = {}
    for p in paths:
        if os.path.isfile(p):
            _log(log_cb, f"  Hashing: {os.path.basename(p)}")
            result[os.path.abspath(p)] = hash_file(p)
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                for fname in sorted(files):
                    fp = os.path.join(root, fname)
                    _log(log_cb, f"  Hashing: {os.path.relpath(fp, p)}")
                    result[os.path.abspath(fp)] = hash_file(fp)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Compression
# ─────────────────────────────────────────────────────────────────────────────

def _level_gz(level: str) -> int:
    return 1 if level == "min" else 9

def _level_zstd(level: str) -> int:
    return 1 if level == "min" else 22

def _level_7z(level: str) -> int:
    return 1 if level == "min" else 9


def compress_paths(
    paths: list[str],
    archive_path: str,
    fmt: str,
    level: str,
    log_cb=None,
) -> bool:
    """
    Compress *paths* (files or directories) into *archive_path*.
    fmt   : "tar.gz" | "tar.zstd" | "7z"
    level : "min" | "max"
    Returns True on success.
    """
    try:
        if fmt == "tar.gz":
            with tarfile.open(archive_path, "w:gz", compresslevel=_level_gz(level)) as tar:
                for p in paths:
                    arcname = os.path.basename(p)
                    _log(log_cb, f"  Packing: {arcname}")
                    tar.add(p, arcname=arcname)
            return True

        elif fmt == "tar.zstd":
            try:
                import zstandard as zstd  # type: ignore
            except ImportError:
                _log(log_cb, "❌ zstandard not installed — run: pip install zstandard")
                return False
            cctx = zstd.ZstdCompressor(level=_level_zstd(level), threads=-1)
            with open(archive_path, "wb") as f_out:
                with cctx.stream_writer(f_out, closefd=False) as compressor:
                    with tarfile.open(fileobj=compressor, mode="w|") as tar:  # type: ignore[arg-type]
                        for p in paths:
                            arcname = os.path.basename(p)
                            _log(log_cb, f"  Packing: {arcname}")
                            tar.add(p, arcname=arcname)
            return True

        elif fmt == "7z":
            try:
                import py7zr  # type: ignore
            except ImportError:
                _log(log_cb, "❌ py7zr not installed — run: pip install py7zr")
                return False
            preset = _level_7z(level)
            filters = [{"id": py7zr.FILTER_LZMA2, "preset": preset}]
            with py7zr.SevenZipFile(archive_path, "w", filters=filters) as z:
                for p in paths:
                    arcname = os.path.basename(p)
                    _log(log_cb, f"  Packing: {arcname}")
                    if os.path.isdir(p):
                        z.writeall(p, arcname)
                    else:
                        z.write(p, arcname)
            return True

        else:
            _log(log_cb, f"❌ Unknown format: {fmt}")
            return False

    except Exception as e:
        _log(log_cb, f"❌ Compression error: {e}")
        return False


def decompress_archive(
    archive_path: str,
    output_dir: str,
    fmt: str,
    log_cb=None,
) -> bool:
    """Extract *archive_path* into *output_dir*. Returns True on success."""
    os.makedirs(output_dir, exist_ok=True)
    try:
        if fmt == "tar.gz":
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(output_dir)
            return True

        elif fmt == "tar.zstd":
            import zstandard as zstd  # type: ignore
            dctx = zstd.ZstdDecompressor()
            with open(archive_path, "rb") as f_in:
                with dctx.stream_reader(f_in) as reader:
                    with tarfile.open(fileobj=reader, mode="r|") as tar:  # type: ignore[arg-type]
                        tar.extractall(output_dir)
            return True

        elif fmt == "7z":
            import py7zr  # type: ignore
            with py7zr.SevenZipFile(archive_path, "r") as z:
                z.extractall(output_dir)
            return True

        else:
            _log(log_cb, f"❌ Unknown format: {fmt}")
            return False

    except Exception as e:
        _log(log_cb, f"❌ Decompression error: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Public DB operations
# ─────────────────────────────────────────────────────────────────────────────

def add_entry(
    description: str,
    source: str,          # "app" | "manual"
    paths: list[str],     # files/folders to snapshot
    fmt: str,
    level: str,
    log_cb=None,
    progress_cb=None,     # (step: int, total: int)
) -> dict | None:
    """
    Hash files, compress into archive, write DB row.
    Returns the new entry dict, or None on failure.
    """
    _ensure_dirs()
    entry_id = str(uuid.uuid4())

    _log(log_cb, f"→ Computing hashes for {len(paths)} path(s)…")
    if progress_cb:
        progress_cb(0, 3)
    hashes = hash_paths(paths, log_cb=log_cb)
    _log(log_cb, f"  {len(hashes)} file(s) hashed.")

    ext          = FORMAT_EXTS.get(fmt, ".tar.gz")
    archive_name = f"{entry_id}{ext}"
    archive_path = str(ARCHIVES_DIR / archive_name)

    _log(log_cb, f"→ Compressing [{fmt} / {level}]…")
    if progress_cb:
        progress_cb(1, 3)

    ok = compress_paths(paths, archive_path, fmt, level, log_cb=log_cb)
    if not ok:
        return None

    size_compressed = os.path.getsize(archive_path) if os.path.exists(archive_path) else 0
    _log(log_cb, f"  Archive: {archive_name}  ({fmt_size(size_compressed)})")

    # Calculate total original size for display
    size_original = sum(
        os.path.getsize(fp) for fp in hashes if os.path.exists(fp)
    )

    entry: dict = {
        "id":               entry_id,
        "timestamp":        datetime.now().isoformat(),
        "description":      description,
        "source":           source,
        "format":           fmt,
        "level":            level,
        "archive":          archive_name,
        "hashes":           hashes,
        "original_paths":   [os.path.abspath(p) for p in paths],
        "size_original":    size_original,
        "size_compressed":  size_compressed,
        "file_count":       len(hashes),
    }

    db = load_db()
    db["entries"].insert(0, entry)   # newest first
    save_db(db)

    if progress_cb:
        progress_cb(3, 3)
    _log(log_cb, f"✅ Snapshot saved  [{entry_id[:8]}…]  {fmt_size(size_compressed)}")
    return entry


def remove_entry(entry_id: str) -> bool:
    """Delete archive file + DB row. Returns True if found."""
    db = load_db()
    entry = next((e for e in db["entries"] if e["id"] == entry_id), None)
    if not entry:
        return False
    archive = ARCHIVES_DIR / entry["archive"]
    if archive.exists():
        archive.unlink()
    db["entries"] = [e for e in db["entries"] if e["id"] != entry_id]
    save_db(db)
    return True


def restore_entry(
    entry_id: str,
    log_cb=None,
    progress_cb=None,
) -> bool:
    """
    Decompress archive → copy each file back to its original path.
    Returns True on full success.
    """
    db = load_db()
    entry = next((e for e in db["entries"] if e["id"] == entry_id), None)
    if not entry:
        _log(log_cb, "❌ Entry not found in database.")
        return False

    archive_path = str(ARCHIVES_DIR / entry["archive"])
    if not os.path.exists(archive_path):
        _log(log_cb, f"❌ Archive missing: {archive_path}")
        return False

    if progress_cb:
        progress_cb(0, 3)

    with tempfile.TemporaryDirectory(prefix="kivotos_undo_") as tmpdir:
        _log(log_cb, f"→ Decompressing archive [{entry['format']}]…")
        ok = decompress_archive(archive_path, tmpdir, entry["format"], log_cb=log_cb)
        if not ok:
            return False

        if progress_cb:
            progress_cb(1, 3)

        orig_paths: list[str] = entry.get("original_paths", [])
        errors = 0

        _log(log_cb, f"→ Restoring {len(orig_paths)} path(s)…")
        for orig in orig_paths:
            base = os.path.basename(orig)
            src  = os.path.join(tmpdir, base)
            if not os.path.exists(src):
                _log(log_cb, f"  ⚠ Not in archive: {base}")
                continue
            try:
                if os.path.isdir(src):
                    if os.path.exists(orig):
                        shutil.rmtree(orig)
                    shutil.copytree(src, orig)
                else:
                    os.makedirs(os.path.dirname(orig) or ".", exist_ok=True)
                    shutil.copy2(src, orig)
                _log(log_cb, f"  ✔ Restored: {orig}")
            except Exception as e:
                _log(log_cb, f"  ❌ Failed: {orig} — {e}")
                errors += 1

        if progress_cb:
            progress_cb(3, 3)

        if errors:
            _log(log_cb, f"\n⚠ Restore finished with {errors} error(s).")
            return False

        _log(log_cb, "\n✅ Restore complete.")
        return True


def get_entry(entry_id: str) -> dict | None:
    db = load_db()
    return next((e for e in db["entries"] if e["id"] == entry_id), None)