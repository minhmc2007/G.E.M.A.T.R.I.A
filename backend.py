"""
backend.py — Kivotos Halo Asset Tool
Core logic: filename parsing, bundle scanning, extraction, repacking.
Windows / Blue Archive JP (+ GL stub) edition.
"""

import os
import re
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

JP_BUNDLE_PATH = r"C:\YostarGames\BlueArchive_JP\BlueArchive_Data\StreamingAssets\AssetBundles"
GL_BUNDLE_PATH = r"C:\YostarGames\BlueArchive\BlueArchive_Data\StreamingAssets\AssetBundles"

_home = Path.home()
DEFAULT_OUTPUT_BASE = str(_home / "G.E.M.A.T.R.I.A_Output" / "extracted")
DEFAULT_REPACK_DIR  = str(_home / "G.E.M.A.T.R.I.A_Output" / "repacked")

SCRIPT_VERSION = "G.E.M.A.T.R.I.A"

# ---------------------------------------------------------------------------
# Display / label maps
# ---------------------------------------------------------------------------

GROUP_LABELS: dict[str, str] = {
    "characters":      "3D Characters",
    "spinecharacters": "Spine Characters",
    "spinelobbies":    "Spine Lobbies",
    "cafe":            "Café",
    "character":       "Story Character",
    "fx":              "Effects",
    "other":           "Other",
}

ASSET_TYPE_LABELS: dict[str, str] = {
    "animationclips":       "Animation Clips",
    "animatorcontrollers":  "Animator Controllers",
    "assets":               "Assets (Meta)",
    "audio":                "Audio",
    "materials":            "Materials",
    "meshes":               "Meshes",
    "prefabs":              "Prefabs",
    "textassets":           "Text Assets",
    "textures":             "Textures",
    "timelines":            "Timelines",
}

# ---------------------------------------------------------------------------
# Filename parser
# ---------------------------------------------------------------------------
# JP bundle filename patterns:
#
#   TYPE A  assets-_mx-{GROUP}-{NAME}-_mxdependency-{ATYPE}-{DATE}_assets_all_{HASH}.bundle
#   TYPE B  {PREFIX}-{NAME}-_mxload-{ATYPE}-{DATE}_assets_all_{HASH}.bundle
#   TYPE C  fx_{NAME}-_mxload-{ATYPE}-{DATE}_assets_all_{HASH}.bundle
#
# PREFIX examples: cafe-characteranimation | character
# NAME   examples: shiroko_original | shiroko_ridingsuit_spr | lobbyshiroko_multi
# ---------------------------------------------------------------------------

_DATE_HASH_RE = re.compile(r"-(\d{4}-\d{2}-\d{2})_assets_all_(\d+)$")


def parse_bundle_filename(filename: str) -> dict:
    """Return a rich metadata dict from a JP BA bundle filename."""
    base = os.path.splitext(filename)[0]   # strip .bundle

    result: dict = {
        "filename":          filename,
        "character":         None,
        "variant":           None,
        "group":             None,
        "group_display":     None,
        "asset_type":        None,
        "asset_type_display": None,
        "date":              None,
        "hash":              None,
        "raw_name":          None,
        "display_name":      filename,
        "tags":              [],
    }

    # ── Strip date/hash suffix ────────────────────────────────────────────
    m = _DATE_HASH_RE.search(base)
    if m:
        result["date"] = m.group(1)
        result["hash"] = m.group(2)
        core = base[: m.start()]
    else:
        core = base

    # ── Split on dependency/load separator ────────────────────────────────
    asset_type: str | None = None
    if "-_mxdependency-" in core:
        left, _, right = core.partition("-_mxdependency-")
        asset_type = right.lower()
    elif "-_mxload-" in core:
        left, _, right = core.partition("-_mxload-")
        asset_type = right.lower()
    else:
        left = core

    result["asset_type"] = asset_type
    result["asset_type_display"] = ASSET_TYPE_LABELS.get(asset_type, (asset_type or "").title())

    # ── Determine group + raw_name from left segment ─────────────────────
    raw_name: str | None = None

    # TYPE A:  assets-_mx-{group}-{name}
    mx = re.match(r"^assets-_mx-([^-]+)-(.+)$", left)
    if mx:
        result["group"] = mx.group(1).lower()
        raw_name = mx.group(2)

    # TYPE B / C: various prefixes before the name
    elif left.startswith("cafe-characteranimation-"):
        result["group"] = "cafe"
        raw_name = left[len("cafe-characteranimation-"):]

    elif left.startswith("character-"):
        result["group"] = "character"
        raw_name = left[len("character-"):]

    elif left.startswith("fx_"):
        result["group"] = "fx"
        raw_name = left[len("fx_"):]

    else:
        # Generic fallback
        result["group"] = (left.split("-")[0] if "-" in left else left.split("_")[0]).lower()
        raw_name = left

    result["group_display"] = GROUP_LABELS.get(result["group"] or "other", (result["group"] or "other").title())
    result["raw_name"] = raw_name

    # ── Parse character + variant from raw_name ───────────────────────────
    if raw_name:
        rn = raw_name

        # Strip "lobby" prefix used in spinelobbies
        if rn.startswith("lobby"):
            rn = rn[len("lobby"):]

        # Strip trailing "_spr" (it's a type marker, not a variant)
        rn = re.sub(r"_spr$", "", rn)

        parts = rn.split("_")
        char   = parts[0].lower() if parts else None
        var_parts = parts[1:] if len(parts) > 1 else []
        variant = "_".join(var_parts) if var_parts else "original"

        result["character"] = char
        result["variant"]   = variant

        char_display    = (char or "Unknown").title()
        variant_display = variant.replace("_", " ").title() if variant != "original" else ""
        result["display_name"] = f"{char_display}" + (f" ({variant_display})" if variant_display else "")

    # ── Build tag list ────────────────────────────────────────────────────
    tags: list[str] = []
    if result["group"]:      tags.append(result["group"])
    if result["character"]:  tags.append(result["character"])
    if result["variant"] and result["variant"] != "original":
        tags.append(result["variant"])
    if result["asset_type"]: tags.append(result["asset_type"])
    result["tags"] = tags

    return result


# ---------------------------------------------------------------------------
# Directory scanner
# ---------------------------------------------------------------------------

def scan_bundles(path: str) -> list[dict]:
    """Scan *path* for .bundle files; return list of metadata dicts."""
    bundles: list[dict] = []
    if not os.path.isdir(path):
        return bundles

    for fname in os.listdir(path):
        if not fname.lower().endswith(".bundle"):
            continue
        fpath = os.path.join(path, fname)
        if not os.path.isfile(fpath):
            continue

        meta = parse_bundle_filename(fname)
        meta["path"] = fpath
        try:
            meta["size"] = os.path.getsize(fpath)
        except OSError:
            meta["size"] = 0
        bundles.append(meta)

    bundles.sort(key=lambda b: (b["character"] or "", b["variant"] or "", b["asset_type"] or ""))
    return bundles


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sanitize_name(name: str) -> str:
    if not name:
        return ""
    return "".join(c for c in name if c.isalnum() or c in " ._-").strip()


def format_size(n: int) -> str:
    if n < 1_024:
        return f"{n} B"
    if n < 1_048_576:
        return f"{n / 1_024:.1f} KB"
    return f"{n / 1_048_576:.2f} MB"


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def extract_bundle(
    bundle_path: str,
    output_dir: str,
    progress_cb=None,
    log_cb=None,
) -> dict:
    """
    Extract all assets from *bundle_path* into *output_dir*.
    Returns {"success": bool, "message": str, "stats": {...}, "output_dir": str}
    """

    def log(msg: str):
        if log_cb:
            log_cb(msg)

    def prog(val: int, total: int):
        if progress_cb:
            progress_cb(val, total)

    try:
        import UnityPy
        from PIL import Image as PILImage
    except ImportError as e:
        return {"success": False, "message": f"Missing dependency: {e}", "stats": {}}

    os.makedirs(output_dir, exist_ok=True)

    try:
        env = UnityPy.load(bundle_path)
    except Exception as e:
        return {"success": False, "message": f"Failed to load bundle: {e}", "stats": {}}

    manifest = {
        "original_bundle_path": os.path.abspath(bundle_path),
        "script_version": SCRIPT_VERSION,
        "assets": [],
    }

    subdirs = {
        "Textures":           os.path.join(output_dir, "Textures"),
        "TextAssets":         os.path.join(output_dir, "TextAssets"),
        "MonoBehaviours_JSON":os.path.join(output_dir, "MonoBehaviours_JSON"),
        "MonoBehaviours_DAT": os.path.join(output_dir, "MonoBehaviours_DAT"),
        "AudioClips":         os.path.join(output_dir, "AudioClips"),
        "OtherAssets":        os.path.join(output_dir, "OtherAssets"),
    }
    for d in subdirs.values():
        os.makedirs(d, exist_ok=True)

    objects = list(env.objects)
    total = len(objects)
    stats = {"total": total, "extracted": 0, "errors": 0, "skipped": 0}
    log(f"Found {total} assets in bundle.")

    for i, obj in enumerate(objects):
        prog(i + 1, total)

        ainfo: dict = {
            "path_id": obj.path_id,
            "type": str(obj.type.name),
            "name": "",
            "extracted_filename": "",
        }

        try:
            data = obj.read()
            raw_name  = getattr(data, "m_Name", "") or ""
            safe_name = sanitize_name(raw_name) or f"{sanitize_name(obj.type.name)}_{obj.path_id}"
            ainfo["name"] = raw_name
            processed = False

            # ── Texture2D / Sprite ────────────────────────────────────────
            if obj.type.name in ("Texture2D", "Sprite"):
                try:
                    img = data.image
                    if img:
                        fname = f"{safe_name}_{obj.path_id}.png"
                        img.save(os.path.join(subdirs["Textures"], fname))
                        ainfo["extracted_filename"] = os.path.join("Textures", fname)
                        processed = True
                except Exception as e:
                    log(f"  ⚠ {obj.type.name} {safe_name}: {e}")

            # ── TextAsset ─────────────────────────────────────────────────
            elif obj.type.name == "TextAsset":
                try:
                    sc = data.script
                    if isinstance(sc, bytes):
                        try:
                            text = sc.decode("utf-8", errors="strict")
                            fname = f"{safe_name}_{obj.path_id}.txt"
                            open(os.path.join(subdirs["TextAssets"], fname), "w", encoding="utf-8").write(text)
                        except (UnicodeDecodeError, ValueError):
                            fname = f"{safe_name}_{obj.path_id}.bytes"
                            open(os.path.join(subdirs["TextAssets"], fname), "wb").write(sc)
                    else:
                        fname = f"{safe_name}_{obj.path_id}.txt"
                        open(os.path.join(subdirs["TextAssets"], fname), "w", encoding="utf-8").write(str(sc))
                    ainfo["extracted_filename"] = os.path.join("TextAssets", fname)
                    processed = True
                except Exception as e:
                    log(f"  ⚠ TextAsset {safe_name}: {e}")

            # ── MonoBehaviour ─────────────────────────────────────────────
            elif obj.type.name == "MonoBehaviour":
                if obj.serialized_type and obj.serialized_type.nodes:
                    try:
                        tree  = obj.read_typetree()
                        fname = f"{safe_name}_{obj.path_id}.json"
                        with open(os.path.join(subdirs["MonoBehaviours_JSON"], fname), "w", encoding="utf-8") as f:
                            json.dump(tree, f, indent=4)
                        ainfo["extracted_filename"] = os.path.join("MonoBehaviours_JSON", fname)
                        processed = True
                    except Exception:
                        pass

                if not processed:
                    try:
                        rb = (getattr(obj, "raw_data", None)
                              or getattr(data, "raw_data", None)
                              or getattr(data, "m_Script", None))
                        if isinstance(rb, bytes):
                            fname = f"{safe_name}_{obj.path_id}.dat"
                            open(os.path.join(subdirs["MonoBehaviours_DAT"], fname), "wb").write(rb)
                            ainfo["extracted_filename"] = os.path.join("MonoBehaviours_DAT", fname)
                            ainfo["type"] = "MonoBehaviour_DAT"
                            processed = True
                    except Exception as e:
                        log(f"  ⚠ MonoBehaviour DAT {safe_name}: {e}")

            # ── AudioClip ─────────────────────────────────────────────────
            elif obj.type.name == "AudioClip":
                try:
                    if data.m_AudioData:
                        res = data.export()
                        if isinstance(res, bytes):
                            fname = f"{safe_name}_{obj.path_id}.wav"
                            open(os.path.join(subdirs["AudioClips"], fname), "wb").write(res)
                        else:
                            fname = f"{safe_name}_{obj.path_id}.audioclipraw"
                            open(os.path.join(subdirs["AudioClips"], fname), "wb").write(data.m_AudioData)
                        ainfo["extracted_filename"] = os.path.join("AudioClips", fname)
                        processed = True
                except Exception as e:
                    log(f"  ⚠ AudioClip {safe_name}: {e}")

            # ── Generic fallback ─────────────────────────────────────────
            if not processed:
                try:
                    rb = (obj.get_raw_data() if hasattr(obj, "get_raw_data") else None) or getattr(obj, "raw_data", None)
                    if rb and isinstance(rb, bytes):
                        fname = f"{safe_name}_{obj.path_id}.genericdat"
                        open(os.path.join(subdirs["OtherAssets"], fname), "wb").write(rb)
                        ainfo["extracted_filename"] = os.path.join("OtherAssets", fname)
                        ainfo["type"] += "_genericdat"
                        processed = True
                except Exception:
                    pass

            if processed:
                stats["extracted"] += 1
            else:
                stats["skipped"] += 1

            if ainfo["extracted_filename"]:
                manifest["assets"].append(ainfo)

        except Exception as e:
            log(f"  ✖ PathID {obj.path_id} ({obj.type.name}): {e}")
            stats["errors"] += 1
            ainfo["extracted_filename"] = "ERROR_EXTRACTING"
            ainfo["name"] = ainfo.get("name") or f"Unknown_{obj.path_id}"
            manifest["assets"].append(ainfo)

    # Write manifest
    mpath = os.path.join(output_dir, "manifest.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

    log(f"\n✅ Done! extracted={stats['extracted']}  skipped={stats['skipped']}  errors={stats['errors']}")
    return {
        "success":    True,
        "message":    "Extraction complete.",
        "stats":      stats,
        "output_dir": output_dir,
    }


# ---------------------------------------------------------------------------
# Repacking
# ---------------------------------------------------------------------------

def repack_bundle(
    input_dir: str,
    output_path: str,
    progress_cb=None,
    log_cb=None,
) -> dict:
    """Repack a previously-extracted directory back into a .bundle."""

    def log(msg: str):
        if log_cb:
            log_cb(msg)

    def prog(val: int, total: int):
        if progress_cb:
            progress_cb(val, total)

    try:
        import UnityPy
        from PIL import Image as PILImage
    except ImportError as e:
        return {"success": False, "message": f"Missing dependency: {e}"}

    manifest_path = os.path.join(input_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        return {"success": False, "message": "manifest.json not found in folder."}

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    orig = manifest.get("original_bundle_path", "")
    if not orig or not os.path.exists(orig):
        return {"success": False, "message": f"Original bundle not found:\n{orig}"}

    try:
        env = UnityPy.load(orig)
    except Exception as e:
        return {"success": False, "message": f"Failed to load original bundle: {e}"}

    assets  = manifest.get("assets", [])
    total   = len(assets)
    modified = 0

    for idx, entry in enumerate(assets):
        prog(idx + 1, total)
        ef = entry.get("extracted_filename", "")
        if not ef or ef == "ERROR_EXTRACTING":
            continue

        mod_file = os.path.join(input_dir, ef)
        if not os.path.exists(mod_file):
            continue

        path_id    = entry["path_id"]
        asset_type = entry["type"]

        target = next((o for o in env.objects if o.path_id == path_id), None)
        if not target:
            continue

        try:
            data    = target.read()
            updated = False

            if asset_type in ("Texture2D", "Sprite"):
                data.image = PILImage.open(mod_file)
                data.save()
                updated = True

            elif asset_type == "TextAsset":
                raw = open(mod_file, "rb").read()
                data.script = raw.decode("utf-8") if isinstance(data.script, str) else raw
                data.save()
                updated = True

            elif asset_type == "MonoBehaviour_JSON":
                tree = json.load(open(mod_file, "r", encoding="utf-8"))
                target.save_typetree(tree)
                updated = True

            elif asset_type == "MonoBehaviour_DAT":
                raw = open(mod_file, "rb").read()
                if hasattr(data, "m_Script") and isinstance(data.m_Script, bytes):
                    data.m_Script = raw; data.save(); updated = True
                elif hasattr(data, "raw_data") and isinstance(data.raw_data, bytes):
                    data.raw_data = raw; data.save(); updated = True

            elif asset_type.startswith("AudioClip"):
                raw = open(mod_file, "rb").read()
                data.m_AudioData = raw
                if hasattr(data, "m_Size"):
                    data.m_Size = len(raw)
                data.save()
                updated = True

            elif asset_type.endswith("_genericdat"):
                raw = open(mod_file, "rb").read()
                if hasattr(target, "raw_data"):
                    target.raw_data = raw
                    updated = True

            if updated:
                modified += 1

        except Exception as e:
            log(f"  ⚠ PathID {path_id}: {e}")

    if modified == 0:
        return {"success": False, "message": "No assets were modified / nothing to repack."}

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(env.file.save())

    log(f"\n✅ Repacked {modified} asset(s) → {output_path}")
    return {
        "success":     True,
        "message":     f"Repacked {modified} asset(s).",
        "output_path": output_path,
    }