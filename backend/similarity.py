from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np


def _to_vec(feature_vector: Any) -> Optional[np.ndarray]:
    if feature_vector is None:
        return None
    arr = np.asarray(feature_vector, dtype="float32")
    if arr.ndim != 1:
        arr = arr.reshape(-1)
    return arr


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0:
        return 0.0
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def find_best_image_match(
    query_features: Iterable[float],
    animals: List[Dict[str, Any]],
) -> Tuple[Optional[Dict[str, Any]], Optional[float]]:
    q_vec = _to_vec(list(query_features))
    if q_vec is None:
        return None, None

    best_animal: Optional[Dict[str, Any]] = None
    best_score: float = -1.0

    for animal in animals:
        vec = _to_vec(animal.get("feature_vector"))
        if vec is None:
            continue
        score = cosine_similarity(q_vec, vec)
        if score > best_score:
            best_score = score
            best_animal = animal

    if best_animal is None:
        return None, None
    return best_animal, best_score


def attribute_similarity(
    query_attrs: Dict[str, Any],
    animal_attrs: Dict[str, Any],
) -> float:
    """
    Very simple overlap-based score.
    - For categorical attributes (e.g., 'diet'), exact match = 1, otherwise 0.
    - For numeric attributes (e.g., legs), score based on closeness.
    Final score is average over all keys in query_attrs.
    """
    if not query_attrs:
        return 0.0

    total = 0.0
    count = 0

    for key, q_val in query_attrs.items():
        if key not in animal_attrs:
            continue
        a_val = animal_attrs[key]
        score = 0.0

        try:
            q_num = float(q_val)
            a_num = float(a_val)
            diff = abs(q_num - a_num)
            score = max(0.0, 1.0 - diff / max(abs(a_num), 1.0))
        except (ValueError, TypeError):
            score = 1.0 if str(q_val).strip().lower() == str(a_val).strip().lower() else 0.0

        total += score
        count += 1

    if count == 0:
        return 0.0
    return total / count


def find_best_attribute_match(
    query_attrs: Dict[str, Any],
    animals: List[Dict[str, Any]],
) -> Tuple[Optional[Dict[str, Any]], Optional[float]]:
    best_animal: Optional[Dict[str, Any]] = None
    best_score: float = -1.0

    for animal in animals:
        score = attribute_similarity(query_attrs, animal.get("attributes") or {})
        if score > best_score:
            best_score = score
            best_animal = animal

    if best_animal is None:
        return None, None
    return best_animal, best_score



