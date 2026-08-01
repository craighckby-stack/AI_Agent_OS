#!/usr/bin/env python3
"""
PIXEL_analyser/analyze.py
Role: Real image color analysis module for the Tessera Enterprise ecosystem.
Integration: Connects to the Diagnostic Engine for telemetry-aware execution.
Dependencies: numpy, PIL, diagnostic_utils_core
"""

import sys
import json
import time
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, Any

# Siphoned diagnostic utilities
from diagnostic_utils_core import DiagnosticResult, generate_telemetry_metadata

def _sanitize(obj: Any) -> Any:
    """Recursively convert numpy scalar types to native Python types for JSON."""
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return _sanitize(obj.tolist())
    return obj

def analyze(image_path: str) -> dict:
    """Run full pixel-level analysis on the given image."""
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)
    h, w, _ = arr.shape
    total_pixels = h * w
    pixels = arr.reshape(-1, 3).astype(np.float32)

    r_mean, g_mean, b_mean = pixels.mean(axis=0)
    r_std, g_std, b_std = pixels.std(axis=0)

    luminance = 0.299 * pixels[:, 0] + 0.587 * pixels[:, 1] + 0.114 * pixels[:, 2]
    lum_min, lum_max, lum_mean, lum_std = float(luminance.min()), float(luminance.max()), float(luminance.mean()), float(luminance.std())

    hist, _ = np.histogram(luminance, bins=10, range=(0, 255))
    hist_pct = [round(float(h) / total_pixels * 100, 2) for h in hist]

    sample_size = min(10000, len(pixels))
    sample = pixels[np.random.choice(len(pixels), sample_size, replace=False)]
    k = 5
    centroids = sample[np.random.choice(len(sample), k, replace=False)].copy()
    for _ in range(10):
        dists = np.linalg.norm(sample[:, None, :] - centroids[None, :, :], axis=2)
        labels = dists.argmin(axis=1)
        new_centroids = np.array([sample[labels == i].mean(axis=0) if (labels == i).any() else centroids[i] for i in range(k)])
        if np.allclose(centroids, new_centroids, atol=1.0): break
        centroids = new_centroids

    full_dists = np.linalg.norm(pixels[:, None, :] - centroids[None, :, :], axis=2)
    full_labels = full_dists.argmin(axis=1)
    dominant_colors = []
    for i in range(k):
        count = int((full_labels == i).sum())
        pct = count / total_pixels * 100
        r, g, b = centroids[i]
        dominant_colors.append({"hex": f"#{int(r):02X}{int(g):02X}{int(b):02X}", "rgb": [round(float(r), 1), round(float(g), 1), round(float(b), 1)], "coverage_pct": round(pct, 2)})
    dominant_colors.sort(key=lambda c: -c["coverage_pct"])

    img_hsv = img.convert("HSV")
    hsv_arr = np.array(img_hsv)
    hues = hsv_arr[:, :, 0].flatten().astype(np.int32)
    sectors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
    hue_buckets = [0] * 6
    for h_val in hues: hue_buckets[min(int(h_val // 43), 5)] += 1
    hue_dist = {sectors[i]: round(hue_buckets[i] / total_pixels * 100, 2) for i in range(6)}

    dominant_sector = max(hue_dist, key=hue_dist.get)
    if dominant_sector == "blue" and hue_dist["blue"] > 30: atmosphere = "sky-dominant"
    elif dominant_sector in ("red", "magenta") and lum_mean > 100: atmosphere = "warm-dominant"
    elif dominant_sector == "green": atmosphere = "vegetation-dominant"
    elif lum_mean < 50: atmosphere = "low-light"
    elif lum_mean > 200: atmosphere = "high-brightness"
    else: atmosphere = f"neutral ({dominant_sector}-leaning)"

    return {
        "module": "pixel_analyzer",
        "image": {"path": image_path, "dimensions": {"width": int(w), "height": int(h)}, "pixel_count": int(total_pixels)},
        "color_stats": {"mean_rgb": {"r": round(r_mean, 2), "g": round(g_mean, 2), "b": round(b_mean, 2)}, "std_rgb": {"r": round(r_std, 2), "g": round(g_std, 2), "b": round(b_std, 2)}},
        "brightness": {"luminance_min": lum_min, "luminance_max": lum_max, "luminance_mean": lum_mean, "luminance_std": lum_std, "histogram_pct": hist_pct},
        "dominant_colors": dominant_colors,
        "hue_distribution_pct": hue_dist,
        "atmospheric_interpretation": atmosphere,
        "metadata": {"analysis_method": "k-means (k=5)", "deterministic": True, "telemetry": generate_telemetry_metadata()}
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python3 analyze.py <image_path>"}), file=sys.stderr)
        sys.exit(1)
    
    start_time = time.perf_counter()
    try:
        if not Path(sys.argv[1]).exists(): raise FileNotFoundError("Image not found")
        report = _sanitize(analyze(sys.argv[1]))
        report["execution_time_ms"] = round((time.perf_counter() - start_time) * 1000, 3)
        print(json.dumps(report, indent=2))
    except Exception as e:
        print(json.dumps({"status": "CRITICAL_FAILURE", "error": str(e)}), file=sys.stderr)
        sys.exit(1)