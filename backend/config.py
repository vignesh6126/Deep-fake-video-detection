import os

# Absolute path to backend directory
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

# Upload folder (ensure it exists)
UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Folder containing .pt models (inside backend now)
PT_MODELS_DIR = os.path.join(BACKEND_DIR, "model", "pt_models")

# Model paths
MODEL_PATHS = {
    "efficientnet_ffpp": {
        "path": os.path.join(PT_MODELS_DIR, "efficientnet_ffpp.pt"),
        "arch": "efficientnet",
    }
}

ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "mkv"}
SAMPLE_EVERY_N_FRAMES = 15
MAX_FRAMES = 40
BATCH_SIZE = 8
MODEL_NAMES = list(MODEL_PATHS.keys())
