import json
import os
import secrets
from typing import Any, Dict

from werkzeug.datastructures import FileStorage


def save_image_file(file: FileStorage, upload_folder: str) -> str:
    ext = os.path.splitext(file.filename or "")[1].lower() or ".jpg"
    safe_name = secrets.token_hex(16) + ext
    os.makedirs(upload_folder, exist_ok=True)
    path = os.path.join(upload_folder, safe_name)
    file.save(path)
    return path


def parse_attributes(raw: Any) -> Dict[str, Any]:
    """
    Normalise attributes from either:
    - a JSON string
    - a dict-like object
    """
    if isinstance(raw, dict):
        return raw
    if raw is None:
        return {}
    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return {}
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid attributes JSON: {exc}") from exc
    raise ValueError("Attributes must be a JSON object or dict.")



