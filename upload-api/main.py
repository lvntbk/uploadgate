from __future__ import annotations
from uuid import uuid4

import os
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

APP_NAME = "uploadgate-upload-api"
UPLOAD_COUNT = 0
DELETE_COUNT = 0

DATA_DIR = Path(os.getenv("DATA_DIR", "/data/uploads"))
# Max upload size in bytes (default 100 MiB)
MAX_UPLOAD_BYTES = int(os.getenv('MAX_UPLOAD_BYTES', str(100 * 1024 * 1024)))

UPLOAD_TOKEN = os.getenv("UPLOAD_TOKEN", "").strip()  # boşsa auth devre dışı (dev ortamı)

app = FastAPI(title=APP_NAME, version="0.1.1")


@app.get("/health")
def health():
    return {"ok": True, "app": APP_NAME}


def _require_token(request: Request) -> None:
    if not UPLOAD_TOKEN:
        return
    provided = (request.headers.get("X-Upload-Token") or "").strip()
    if not provided or provided != UPLOAD_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


def _safe_target_path(base_dir: Path, rel_path: str) -> Path:
    if not rel_path or rel_path.endswith("/"):
        raise HTTPException(status_code=400, detail="Invalid filename")
    if rel_path.startswith("/") or rel_path.startswith("\\"):
        raise HTTPException(status_code=400, detail="Absolute paths are not allowed")
    if "\x00" in rel_path:
        raise HTTPException(status_code=400, detail="Invalid path")

    base_dir = base_dir.resolve()
    target = (base_dir / rel_path).resolve()

    try:
        common = os.path.commonpath([str(base_dir), str(target)])
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid path")

    if common != str(base_dir):
        raise HTTPException(status_code=400, detail="Path traversal detected")

    return target


@app.put("/upload/{filename:path}")
async def upload(filename: str, request: Request, overwrite: bool = False):
    _require_token(request)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Randomize stored filename to avoid predictable names on disk
    # Keep directory prefix, randomize only the basename
    import os
    orig = filename
    d = os.path.dirname(orig)
    base = os.path.basename(orig)
    _, ext = os.path.splitext(base)
    rnd = f"{uuid4().hex}{ext.lower()}"
    stored_as = os.path.join(d, rnd) if d else rnd
    target_path = _safe_target_path(DATA_DIR, stored_as)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if target_path.exists() and not overwrite:
        raise HTTPException(status_code=409, detail="File already exists (use ?overwrite=true)")

    # STREAMING: RAM'e komple alma, chunk chunk yaz
    try:
        total_bytes = 0
        with open(target_path, "wb") as f:
            async for chunk in request.stream():
                if chunk:
                    total_bytes += len(chunk)
                    if total_bytes > MAX_UPLOAD_BYTES:
                        # delete partial file to avoid leaving junk on disk
                        try:
                            f.close()
                        except Exception:
                            pass
                        try:
                            target_path.unlink(missing_ok=True)
                        except Exception:
                            pass
                        raise HTTPException(status_code=413, detail=f"File too large (max {MAX_UPLOAD_BYTES} bytes)")
                    f.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Write failed: {e}")

    global UPLOAD_COUNT
    UPLOAD_COUNT += 1
    return JSONResponse({"ok": True, "original": filename, "stored_as": stored_as, "saved_to": str(target_path)})




@app.delete("/files/{filename:path}")
async def delete_file(filename: str, request: Request):
    _require_token(request)
    target_path = _safe_target_path(DATA_DIR, filename)

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Not found")

    if target_path.is_dir():
        raise HTTPException(status_code=400, detail="Cannot delete a directory")

    try:
        target_path.unlink()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {e}")

    global DELETE_COUNT
    DELETE_COUNT += 1
    return {"ok": True, "deleted": str(target_path)}


@app.get("/list")
async def list_files(prefix: str = "", limit: int = 200):
    if limit < 1 or limit > 2000:
        raise HTTPException(status_code=400, detail="limit must be 1..2000")

    base = DATA_DIR.resolve()

    # prefix verilirse: base/prefix altında listeler (prefix dosyaysa parent alınır)
    if prefix:
        start = _safe_target_path(base, prefix)
        root = start if start.is_dir() else start.parent
    else:
        root = base

    if not root.exists():
        return {"ok": True, "items": [], "count": 0}

    items = []
    try:
        for fp in root.rglob("*"):
            if fp.is_file():
                rel = fp.resolve().as_posix().replace(base.as_posix() + "/", "")
                items.append(rel)
                if len(items) >= limit:
                    break
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List failed: {e}")

    return {"ok": True, "items": items, "count": len(items)}


@app.get("/metrics")
async def metrics():
    return {"uploads": UPLOAD_COUNT, "deletes": DELETE_COUNT}