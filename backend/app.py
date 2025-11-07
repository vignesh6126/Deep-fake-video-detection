import os
import uuid
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from config import UPLOAD_DIR, ALLOWED_EXTENSIONS, SAMPLE_EVERY_N_FRAMES, MAX_FRAMES, MODEL_NAMES, MODEL_PATHS
from video_utils import allowed_file, sample_frames, frame_to_base64_bgr
from detector import DeepfakeDetector
import torch

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB max upload

# Lazy load detectors dictionary for all models
detectors = {}

def get_detector(model_name):
    global detectors
    if model_name not in detectors:
        if model_name not in MODEL_PATHS:
            raise ValueError(f"Unknown model '{model_name}'. Available: {MODEL_NAMES}")
        detectors[model_name] = DeepfakeDetector(
            model_path=MODEL_PATHS[model_name]["path"], 
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
    return detectors[model_name]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "no file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "no selected file"}), 400

        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({"error": f"allowed extensions: {ALLOWED_EXTENSIONS}"}), 400

        # Get selected model from request form, default to first model
        model_name = request.form.get("model_name", MODEL_NAMES[0])

        filename = secure_filename(file.filename)
        uid = str(uuid.uuid4())[:8]
        saved_name = f"{uid}_{filename}"
        saved_path = os.path.join(UPLOAD_DIR, saved_name)
        file.save(saved_path)

        # Sample frames
        frames = sample_frames(saved_path, every_n=SAMPLE_EVERY_N_FRAMES, max_frames=MAX_FRAMES, resize=(256,256))
        if not frames:
            return jsonify({"error": "no frames extracted"}), 400

        # Get detector for the chosen model
        det = get_detector(model_name)
        scores = det.predict_frames(frames)
        agg = det.aggregate(scores)

        # Prepare sample thumbnails (first 6 frames)
        thumbnails = []
        for i, f in enumerate(frames[:6]):
            thumbnails.append({
                "index": i,
                "img_b64": frame_to_base64_bgr(f),
                "score": scores[i] if i < len(scores) else None
            })

        response = {
            "filename": filename,
            "model_used": model_name,
            "num_frames": len(frames),
            "frame_scores": scores,
            "aggregate": agg,
            "thumbnails": thumbnails
        }
        return jsonify(response), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
