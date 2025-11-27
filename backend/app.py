import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from .database import (
    init_db,
    get_all_animals,
    insert_animal,
)
from .resnet_model import get_feature_vector_from_file
from .similarity import (
    find_best_image_match,
    find_best_attribute_match,
)
from .utils import (
    save_image_file,
    parse_attributes,
)
# Gemini removed - using only ResNet50 for classification


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, static_folder=None)
    CORS(app)

    # Basic configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE_PATH=os.path.join(
            os.path.dirname(__file__),
            "animals.db",
        ),
        UPLOAD_FOLDER=os.path.join(
            os.path.dirname(__file__),
            "..",
            "frontend",
            "uploads",
        ),
    )

    if test_config:
        app.config.update(test_config)

    # Ensure folders / DB exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    init_db(app.config["DATABASE_PATH"])

    # Global error handler to ensure JSON responses
    @app.errorhandler(500)
    def handle_500(e):
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"error": "Endpoint not found"}), 404

    # ---- Static frontend routes ----

    FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

    @app.route("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/main")
    def main_page():
        return send_from_directory(FRONTEND_DIR, "main.html")

    @app.route("/static/<path:filename>")
    def static_files(filename: str):
        return send_from_directory(FRONTEND_DIR, filename)

    # ---- API: Image classification ----

    @app.route("/api/classify-image", methods=["POST"])
    def classify_image():
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        image_path = save_image_file(file, app.config["UPLOAD_FOLDER"])
        features = get_feature_vector_from_file(image_path)

        animals = get_all_animals(app.config["DATABASE_PATH"])
        best_match, best_score = find_best_image_match(features, animals)

        response = {
            "mode": "resnet",
            "match_score": best_score,
        }

        # Threshold for "confident" similarity (lowered to 0.5 for better matching)
        if best_match and best_score is not None and best_score >= 0.5:
            response["source"] = "database"
            response["animal"] = best_match
            return jsonify(response)

        # No match found - return message suggesting to add the animal
        return jsonify({
            "error": "No similar animal found in database",
            "message": "The uploaded image doesn't match any animal in FAUNARA's database. Consider adding this animal using the 'Improve Faunara' section.",
            "match_score": best_score,
            "suggestion": "Add this animal to help FAUNARA learn"
        }), 404

    # ---- API: Attribute classification ----

    @app.route("/api/classify-attributes", methods=["POST"])
    def classify_attributes():
        data = request.get_json(silent=True) or {}
        raw_attrs = data.get("attributes", {})

        attrs = parse_attributes(raw_attrs)
        animals = get_all_animals(app.config["DATABASE_PATH"])
        best_match, best_score = find_best_attribute_match(attrs, animals)

        if not best_match:
            return jsonify({"error": "No animals in database to compare"}), 404

        return jsonify(
            {
                "mode": "attributes",
                "match_score": best_score,
                "animal": best_match,
            }
        )

    # ---- API: Improve Faunara (add animal) ----

    @app.route("/api/improve-faunara", methods=["POST"])
    def improve_faunara():
        try:
            name = request.form.get("name")
            habitat = request.form.get("habitat", "")
            facts = request.form.get("facts", "")
            raw_attrs = request.form.get("attributes", "{}")

            if not name:
                return jsonify({"error": "Name is required"}), 400

            try:
                attrs = parse_attributes(raw_attrs)
            except ValueError as exc:
                return jsonify({"error": str(exc)}), 400

            image_path = None
            features = None

            if "image" in request.files and request.files["image"].filename:
                try:
                    file = request.files["image"]
                    image_path = save_image_file(file, app.config["UPLOAD_FOLDER"])
                    features = get_feature_vector_from_file(image_path)
                except Exception as exc:
                    return jsonify({"error": f"Failed to process image: {str(exc)}"}), 500

            try:
                animal_id = insert_animal(
                    db_path=app.config["DATABASE_PATH"],
                    name=name,
                    habitat=habitat,
                    facts=facts,
                    attributes=attrs,
                    image_path=image_path,
                    feature_vector=features,
                )
            except Exception as exc:
                return jsonify({"error": f"Failed to save animal to database: {str(exc)}"}), 500

            return jsonify(
                {
                    "message": "Animal added to Faunara",
                    "id": animal_id,
                }
            )
        except Exception as exc:
            return jsonify({"error": f"Unexpected error: {str(exc)}"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)


