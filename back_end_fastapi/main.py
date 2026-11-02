from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps

DATASET_ROOT = Path(os.getenv("PLANT_DATASET_PATH", Path.home() / ".cache" / "kagglehub" / "datasets" / "sujallimje" / "plant-pathogens"))
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024

DISEASE_GUIDES = {
    "healthy": {
        "description": "The leaf appears healthy and shows no evident disease damage.",
        "severity": "None",
        "treatment": "Continue regular watering and balanced nutrition. Inspect plants weekly.",
    },
    "early_blight": {
        "description": "A fungal disease that commonly causes dark, target-shaped spots on lower leaves.",
        "severity": "Moderate",
        "treatment": "Remove affected leaves, avoid overhead watering, and apply an appropriate registered fungicide.",
    },
    "late_blight": {
        "description": "A destructive water-borne disease that produces dark lesions and pale fungal growth.",
        "severity": "High",
        "treatment": "Remove infected tissue promptly and use a copper-based or locally recommended fungicide.",
    },
    "leaf_mold": {
        "description": "A fungal disease that can produce pale spots and mold on leaf surfaces.",
        "severity": "Moderate",
        "treatment": "Improve ventilation, reduce humidity, and remove heavily affected leaves.",
    },
    "bacterial_spot": {
        "description": "A bacterial infection associated with small dark, water-soaked leaf lesions.",
        "severity": "High",
        "treatment": "Remove infected material, avoid working with wet plants, and use a registered copper treatment.",
    },
    "powdery_mildew": {
        "description": "A fungal infection that appears as white powder-like patches on leaves.",
        "severity": "Moderate",
        "treatment": "Improve airflow and apply neem oil or a fungicide approved for your crop.",
    },
    "rust": {
        "description": "A fungal disease that produces orange, brown, or rust-colored pustules.",
        "severity": "Moderate",
        "treatment": "Remove infected leaves and apply an appropriate rust fungicide at the first sign.",
    },
    "yellow_leaf_curl_virus": {
        "description": "A viral disease commonly linked to curled, yellowing leaves.",
        "severity": "High",
        "treatment": "Remove infected plants and control whiteflies. There is no cure for infected plants.",
    },
}

app = FastAPI(title="Plant Pathology Detection API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def clean_label(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_").replace("__", "_")


def display_label(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").title()


def find_image_classes() -> Dict[str, List[Path]]:
    if not DATASET_ROOT.exists():
        return {}

    extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    classes: Dict[str, List[Path]] = {}
    for directory in DATASET_ROOT.rglob("*"):
        if not directory.is_dir():
            continue
        images = [p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in extensions]
        if images:
            label = clean_label(directory.name)
            classes.setdefault(label, []).extend(images)
    return classes


def image_features(path: Path) -> np.ndarray | None:
    try:
        with Image.open(path) as image:
            image = ImageOps.exif_transpose(image).convert("RGB")
            image.thumbnail((96, 96))
            pixels = np.asarray(image, dtype=np.float32) / 255.0
            rgb_mean = pixels.mean(axis=(0, 1))
            rgb_std = pixels.std(axis=(0, 1))

            hsv = image.convert("HSV")
            hsv_pixels = np.asarray(hsv.resize((64, 64)), dtype=np.float32) / 255.0
            hue_hist, _ = np.histogram(hsv_pixels[:, :, 0], bins=12, range=(0, 1))
            saturation_hist, _ = np.histogram(hsv_pixels[:, :, 1], bins=8, range=(0, 1))
            hist = np.concatenate((hue_hist, saturation_hist)).astype(np.float32)
            hist /= max(hist.sum(), 1)
            return np.concatenate((rgb_mean, rgb_std, hist))
    except (OSError, ValueError):
        return None


CLASS_PROFILES: Dict[str, np.ndarray] = {}
CLASS_COUNTS: Dict[str, int] = {}


def build_profiles() -> None:
    CLASS_PROFILES.clear()
    CLASS_COUNTS.clear()
    for label, images in find_image_classes().items():
        vectors = [v for path in images[:120] if (v := image_features(path)) is not None]
        if vectors:
            CLASS_PROFILES[label] = np.mean(vectors, axis=0)
            CLASS_COUNTS[label] = len(images)


build_profiles()


def guide_for(label: str) -> dict:
    exact = DISEASE_GUIDES.get(label)
    if exact:
        return exact
    return {
        "description": f"Detected as {display_label(label)} using similarity to the downloaded dataset.",
        "severity": "Unknown",
        "treatment": "Isolate affected plants and consult a local plant-health specialist for crop-specific treatment.",
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "dataset_root": str(DATASET_ROOT),
        "dataset_loaded": bool(CLASS_PROFILES),
        "classes_loaded": len(CLASS_PROFILES),
        "images_indexed": sum(CLASS_COUNTS.values()),
    }


@app.get("/api/diseases")
def diseases():
    return {
        "classes": [
            {
                "id": label,
                "name": display_label(label),
                "image_count": CLASS_COUNTS[label],
                "description": guide_for(label)["description"],
            }
            for label in sorted(CLASS_PROFILES)
        ]
    }


@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(415, "Upload a JPG, PNG, or WebP image.")
    data = await file.read(MAX_FILE_SIZE + 1)
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(413, "Image must be smaller than 10 MB.")
    if not data:
        raise HTTPException(400, "The uploaded image is empty.")

    import io

    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
        image = ImageOps.exif_transpose(image)
        features = image_features(Path("/tmp/nonexistent.jpg")) if False else None
    except (OSError, ValueError):
        raise HTTPException(400, "The file is not a readable image.")

    image.thumbnail((96, 96))
    pixels = np.asarray(image, dtype=np.float32) / 255.0
    rgb_mean = pixels.mean(axis=(0, 1))
    rgb_std = pixels.std(axis=(0, 1))
    hsv_pixels = np.asarray(image.convert("HSV").resize((64, 64)), dtype=np.float32) / 255.0
    hue_hist, _ = np.histogram(hsv_pixels[:, :, 0], bins=12, range=(0, 1))
    sat_hist, _ = np.histogram(hsv_pixels[:, :, 1], bins=8, range=(0, 1))
    hist = np.concatenate((hue_hist, sat_hist)).astype(np.float32)
    hist /= max(hist.sum(), 1)
    features = np.concatenate((rgb_mean, rgb_std, hist))

    if not CLASS_PROFILES:
        # Dataset-independent response remains useful while setup is being completed.
        return {
            "status": "demo",
            "label": "dataset_not_loaded",
            "name": "Dataset not loaded",
            "confidence": 0,
            "description": "The FastAPI service is running, but the Kaggle dataset path has not been configured or downloaded.",
            "severity": "Unknown",
            "treatment": "Download the dataset and restart the API with PLANT_DATASET_PATH set to its folder.",
        }

    distances = {
        label: float(np.linalg.norm(features - profile))
        for label, profile in CLASS_PROFILES.items()
    }
    ranked = sorted(distances, key=distances.get)[:3]
    best = ranked[0]
    confidence = max(0.0, min(99.9, (1.0 / (1.0 + distances[best])) * 100))
    alternatives = [
        {"name": display_label(label), "confidence": round(max(0.0, 100 / (1 + distances[label])), 1)}
        for label in ranked[1:]
    ]
    return {
        "status": "success",
        "label": best,
        "name": display_label(best),
        "confidence": round(confidence, 1),
        "alternatives": alternatives,
        **guide_for(best),
    }
