from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

APP_NAME = "uploadgate-upload-api"
DATA_DIR = Path(os.getenv("DATA_DIR", "/data/uploads"))

app = FastAPI(title=APP_NAME, version="0.1.0")


@app.get("/health")
def health():
    return {"ok": True, "app": APP_NAME}


@app.put("/upload/{filename:path}")
async def upload(filename: str, request: Request):
    if not filename or filename.endswith("/"):
        raise HTTPException(status_code=400, detail="Invalid filename")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    target_path = DATA_DIR / filename
    target_path.parent.mkdir(parents=True, exist_ok=True)

    body = await request.body()
    # Çok büyük dosya için streaming'e geçeriz (ileride). Şimdilik MVP.
    with open(target_path, "wb") as f:
        f.write(body)

    return JSONResponse({"ok": True, "saved_to": str(target_path)})
