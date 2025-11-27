## FAUNARA: A new way of classifying fauna

FAUNARA is an intelligent wildlife explorer that can:

- **Identify animals from images** using ResNet50 feature extraction and similarity matching against a local SQLite database.
- **Guess animals from attributes** such as legs, skin type, and diet.
- **Learn new animals over time** via a "Improve Faunara" learning mode.
- **Store all knowledge in SQLite**, including attributes, habitat, facts, image paths, and 2048‑dim feature vectors.

### Tech stack

- **Frontend**: HTML, Tailwind CSS (via CDN), vanilla JS, custom jungle‑themed `styles.css`
- **Backend**: Flask (Python), CORS enabled
- **ML**: ResNet50 (TensorFlow / Keras) for feature extraction and similarity matching
- **Database**: SQLite (`animals` table)

### Project structure

- `frontend/`
  - `index.html` – landing page (jungle theme, “Get Started” button)
  - `main.html` – main interface (image classifier, attribute classifier, improve mode)
  - `script.js` – connects UI to Flask APIs
  - `styles.css` – jungle-themed styling and animations
- `backend/`
  - `app.py` – Flask app + API routes
  - `database.py` – SQLite helpers and schema (`animals` table)
  - `resnet_model.py` – ResNet50 feature extraction
  - `gemini_api.py` – (Not used - Gemini integration removed)
  - `similarity.py` – cosine and attribute similarity utilities
  - `utils.py` – image saving and attribute parsing helpers
- `app.py` – top‑level entry point (`flask` app instance)
- `requirements.txt` – backend dependencies

### SQLite schema

Table: `animals`

- **id** – INTEGER PRIMARY KEY AUTOINCREMENT
- **name** – TEXT (animal name, required)
- **habitat** – TEXT (short description)
- **facts** – TEXT (fun facts paragraph)
- **attributes** – TEXT (JSON object as string)
- **image_path** – TEXT (path to stored image file)
- **feature_vector** – TEXT (JSON list of 2048 floats from ResNet50)

### Running FAUNARA locally

1. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   source venv/Scripts/activate  # on Windows PowerShell: venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Gemini** (optional but recommended for full functionality):

   - Create a Gemini API key in your Google Cloud / AI Studio account.
   - Set the environment variable:

   ```bash
   set GEMINI_API_KEY=YOUR_KEY_HERE  # PowerShell / cmd on Windows
   ```

4. **Run the Flask app**:

   ```bash
   python app.py
   ```

   By default this starts the server at `http://localhost:5000`.

5. **Open the UI**:

   - Landing page: `http://localhost:5000/`
   - Main interface: `http://localhost:5000/main`

### Core flows

- **Image classification**
  - User uploads an image on `main.html`.
  - Backend extracts a 2048‑dim feature vector using ResNet50.
  - Cosine similarity is computed against all stored `feature_vector`s in SQLite.
  - If a high‑similarity match is found → return that animal.
  - Otherwise → call Gemini Vision to identify the animal; if new, use Gemini Text to generate habitat + facts and offer to store it via the “Improve Faunara” flow.

- **Attribute classifier**
  - User selects attributes in the Attribute Classifier panel.
  - Backend compares the submitted attribute dict to stored `attributes` in SQLite.
  - The closest match (simple overlap/score) is returned with habitat + facts.

- **Improve Faunara (learning mode)**
  - User fills name, habitat, facts, attributes JSON, and optional image.
  - Backend stores everything in SQLite and, if an image is provided, also stores a ResNet50 feature vector.
  - Future image/attribute queries can now match this new species.

### Notes

- On first run, SQLite database and table are created automatically.
- ResNet50 weights will be downloaded the first time `resnet_model.py` is used.
- If `GEMINI_API_KEY` is not set, Gemini‑related calls will fail; offline similarity still works for any animals that exist in the local database.


