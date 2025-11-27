import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import numpy as np


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS animals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                habitat TEXT,
                facts TEXT,
                attributes TEXT,
                image_path TEXT,
                feature_vector TEXT
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def _row_to_animal(row: sqlite3.Row) -> Dict[str, Any]:
    attributes = json.loads(row["attributes"]) if row["attributes"] else {}
    feature_vector = json.loads(row["feature_vector"]) if row["feature_vector"] else None
    return {
        "id": row["id"],
        "name": row["name"],
        "habitat": row["habitat"],
        "facts": row["facts"],
        "attributes": attributes,
        "image_path": row["image_path"],
        "feature_vector": feature_vector,
    }


def get_all_animals(db_path: str) -> List[Dict[str, Any]]:
    conn = _connect(db_path)
    try:
        cur = conn.execute("SELECT * FROM animals")
        rows = cur.fetchall()
        return [_row_to_animal(r) for r in rows]
    finally:
        conn.close()


def insert_animal(
    db_path: str,
    name: str,
    habitat: str,
    facts: str,
    attributes: Dict[str, Any],
    image_path: Optional[str],
    feature_vector: Optional[Iterable[float]],
) -> int:
    conn = _connect(db_path)
    try:
        # Convert feature_vector to list of native Python floats for JSON serialization
        feature_vector_json = None
        if feature_vector is not None:
            if isinstance(feature_vector, np.ndarray):
                # Convert numpy array to list of native Python floats
                feature_vector_json = json.dumps([float(x) for x in feature_vector.tolist()])
            else:
                # Convert any iterable to list of native Python floats
                feature_vector_json = json.dumps([float(x) for x in feature_vector])
        
        cur = conn.execute(
            """
            INSERT INTO animals (name, habitat, facts, attributes, image_path, feature_vector)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                habitat,
                facts,
                json.dumps(attributes or {}),
                image_path,
                feature_vector_json,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


