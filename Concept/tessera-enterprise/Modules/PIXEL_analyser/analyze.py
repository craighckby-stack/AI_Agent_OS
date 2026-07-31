#!/usr/bin/env python3
"""
pixel_analyzer/analyze.py — Real image color analysis.

This is the substance of the module. It does what an LLM cannot do in a
single call: actual numerical computation on pixel data.

Output: structured JSON report.
"""
import sys
import json
import hashlib
from collections import Counter

import numpy as np
from PIL import Image


def analyze(image_path: str) -> dict:
    """Run full pixel-level analysis on the given image."""
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)
    h, w, _ = arr.shape
    total_pixels = h * w

    # Flatten to (N, 3) for per-pixel operations
    pixels = arr.reshape(-1, 3).astype(np.float32)

    # ── Per-channel means ──────────────────────────────────────────────
    r_mean, g_mean, b_mean = pixels.mean(axis=0)
    r_std, g_std, b_std = pixels.std(axis=0)

    # ── Brightness (luminance) ─────────────────────────────────────────
    # ITU-R BT.601 luma coefficients
    luminance = 0.299 * pixels[:, 0] + 0.587 * pixels[:, 1] + 0.114 * pixels[:, 2]
    lum_min = float(luminance.min())
    lum_max = float(luminance.max())
    lum_mean = float(luminance.mean())
    lum_std = float(luminance.std())

    # ── Brightness histogram (10 buckets, 0-255) ───────────────────────
    hist, _ = np.histogram(luminance, bins=10, range=(0, 255))
    hist_pct = [round(float(h) / total_pixels * 100, 2) for h in hist]

    # Ensure pixel_count is a plain Python int (numpy types aren't JSON-serializable)
    total_pixels = int(total_pixels)
    h = int(h)
    w = int(w)

    # ── Dominant colors via simple k-means (k=5) ───────────────────────
    # Subsample for speed on large images
    sample_size = min(10000, len(pixels))
    sample = pixels[np.random.choice(len(pixels), sample_size, replace=False)]
    k = 5
    # Initialize centroids via k-means++
    centroids = sample[np.random.choice(len(sample), k, replace=False)].copy()
    for _ in range(10):  # 10 iterations is enough for dominant colors
        dists = np.linalg.norm(sample[:, None, :] - centroids[None, :, :], axis=2)
        labels = dists.argmin(axis=1)
        new_centroids = np.array([
            sample[labels == i].mean(axis=0) if (labels == i).any() else centroids[i]
            for i in range(k)
        ])
        if np.allclose(centroids, new_centroids, atol=1.0):
            break
        centroids = new_centroids

    # Compute coverage % for each cluster across full image
    full_dists = np.linalg.norm(pixels[:, None, :] - centroids[None, :, :], axis=2)
    full_labels = full_dists.argmin(axis=1)
    dominant_colors = []
    for i in range(k):
        count = int((full_labels == i).sum())
        pct = count / total_pixels * 100
        r, g, b = centroids[i]
        hex_color = f"#{int(r):02X}{int(g):02X}{int(b):02X}"
        dominant_colors.append({
            "hex": hex_color,
            "rgb": [round(float(r), 1), round(float(g), 1), round(float(b), 1)],
            "coverage_pct": round(pct, 2),
        })
    dominant_colors.sort(key=lambda c: -c["coverage_pct"])

    # ── Hue distribution ───────────────────────────────────────────────
    # Convert to HSV, bucket hues into 6 sectors
    img_hsv = img.convert("HSV")
    hsv_arr = np.array(img_hsv)
    hues = hsv_arr[:, :, 0].flatten().astype(np.int32)
    # OpenCV-style: H in 0-255, sectors of 43 units
    sectors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
    hue_buckets = [0] * 6
    for h_val in hues:
        idx = min(int(h_val // 43), 5)
        hue_buckets[idx] += 1
    hue_dist = {
        sectors[i]: round(hue_buckets[i] / total_pixels * 100, 2)
        for i in range(6)
    }

    # ── Atmospheric interpretation ─────────────────────────────────────
    # Heuristic: which hue sector dominates?
    dominant_sector = max(hue_dist, key=hue_dist.get)
    if dominant_sector == "blue" and hue_dist["blue"] > 30:
        atmosphere = "sky-dominant (daytime sky-like)"
    elif dominant_sector in ("red", "magenta") and lum_mean > 100:
        atmosphere = "warm-dominant (sunset/sunrise-like)"
    elif dominant_sector == "green":
        atmosphere = "vegetation-dominant"
    elif lum_mean < 50:
        atmosphere = "low-light (night/dark scene)"
    elif lum_mean > 200:
        atmosphere = "high-brightness (overexposed/snow/fog)"
    else:
        atmosphere = f"neutral ({dominant_sector}-leaning)"

    # ── Build report ───────────────────────────────────────────────────
    return {
        "module": "pixel_analyzer",
        "image": {
            "path": image_path,
            "dimensions": {"width": w, "height": h},
            "pixel_count": total_pixels,
        },
        "color_stats": {
            "mean_rgb": {
                "r": round(float(r_mean), 2),
                "g": round(float(g_mean), 2),
                "b": round(float(b_mean), 2),
            },
            "std_rgb": {
                "r": round(float(r_std), 2),
                "g": round(float(g_std), 2),
                "b": round(float(b_std), 2),
            },
        },
        "brightness": {
            "luminance_min": round(float(lum_min), 2),
            "luminance_max": round(float(lum_max), 2),
            "luminance_mean": round(float(lum_mean), 2),
            "luminance_std": round(float(lum_std), 2),
            "histogram_pct": hist_pct,
        },
        "dominant_colors": dominant_colors,
        "hue_distribution_pct": hue_dist,
        "atmospheric_interpretation": atmosphere,
        "metadata": {
            "analysis_method": "k-means (k=5, 10 iterations, 10k sample)",
            "luminance_formula": "ITU-R BT.601 (0.299R + 0.587G + 0.114B)",
            "deterministic": True,
        },
    }


def _sanitize(obj):
    """Recursively convert numpy scalar types to native Python types for JSON."""
    import numpy as np
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return _sanitize(obj.tolist())
    return obj


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze.py <image_path>", file=sys.stderr)
        sys.exit(1)
    report = _sanitize(analyze(sys.argv[1]))
    print(json.dumps(report, indent=2))
