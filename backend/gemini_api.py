import os
from typing import Tuple

import google.generativeai as genai


def _configure_client() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set.")
    genai.configure(api_key=api_key)


def identify_animal_from_image(image_path: str) -> str | None:
    """
    Use Gemini Vision to identify an animal from an image.

    Returns the best animal name guess, or None if uncertain.
    """
    _configure_client()
    
    # Try different model names in order of preference
    model_names = ["gemini-pro", "gemini-1.5-pro", "gemini-2.0-flash"]
    model = None
    
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            break
        except Exception:
            continue
    
    if model is None:
        raise RuntimeError(f"Could not initialize any Gemini model. Tried: {', '.join(model_names)}")

    with open(image_path, "rb") as f:
        img_bytes = f.read()

    prompt = (
        "You are an expert zoologist. Look at this image and respond with ONLY the common "
        "animal name in English (e.g., 'African elephant', 'Bald eagle'). "
        "If you are not at least 80% confident, respond with 'unknown'."
    )

    try:
        response = model.generate_content(
            [
                prompt,
                {"mime_type": "image/jpeg", "data": img_bytes},
            ]
        )
        text = (response.text or "").strip()
        if not text or text.lower().startswith("unknown"):
            return None
        return text
    except Exception as e:
        raise RuntimeError(f"Gemini Vision API error: {str(e)}")


def get_habitat_and_facts(animal_name: str) -> Tuple[str, str]:
    """
    Use Gemini Text model to describe habitat and provide fun facts.
    """
    _configure_client()
    
    # Try different model names in order of preference
    model_names = ["gemini-pro", "gemini-1.5-pro", "gemini-2.0-flash"]
    model = None
    
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            break
        except Exception:
            continue
    
    if model is None:
        raise RuntimeError(f"Could not initialize any Gemini model. Tried: {', '.join(model_names)}")

    prompt = (
        f"Give a short, student-friendly description of the typical habitat and 3–5 fun facts "
        f"about the animal '{animal_name}'. "
        "Respond in JSON with two keys: habitat (1–2 sentences) and facts (single paragraph)."
    )

    try:
        response = model.generate_content(prompt)
        text = (response.text or "").strip()
    except Exception as e:
        raise RuntimeError(f"Gemini Text API error: {str(e)}")

    # Best-effort parsing without hard dependency on strict JSON
    habitat = ""
    facts = ""

    if '"habitat"' in text or '"facts"' in text:
        try:
            import json

            data = json.loads(text)
            habitat = data.get("habitat", "")
            facts = data.get("facts", "")
        except Exception:
            pass

    if not habitat or not facts:
        # Fallback: just use the raw text in the facts field
        habitat = habitat or f"The natural habitat of {animal_name} varies across the world."
        facts = facts or text

    return habitat, facts


