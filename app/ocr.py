"""
FoodLens AI - Computer Vision & OCR Module
Performs OpenCV-based image preprocessing and text extraction using RapidOCR (PaddleOCR ONNX engine).
"""

import os
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
from rapidocr_onnxruntime import RapidOCR

# Lazy singleton OCR instance to optimize memory and startup time
_ocr_engine = None

def get_ocr_engine() -> RapidOCR:
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = RapidOCR()
    return _ocr_engine


def preprocess_image(image_path: str) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Applies image preprocessing pipeline using OpenCV:
    1. Read original image
    2. Resize to optimal scale if image is too large/small
    3. Grayscale conversion
    4. Contrast enhancement using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    5. Noise removal / Bilateral Filter
    6. Sharpening kernel
    7. Deskewing / Rotation correction if angle detected
    
    Returns: (original_bgr, preprocessed_bgr, metadata)
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    # Read image with OpenCV, falling back to Pillow for robust WEBP / format decoding
    original = cv2.imread(image_path)
    if original is None:
        try:
            from PIL import Image
            pil_img = Image.open(image_path).convert("RGB")
            original = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except Exception:
            pass

    if original is None:
        raise ValueError(f"Could not decode image (format may be unsupported or corrupted): {image_path}")

    h, w = original.shape[:2]
    metadata = {
        "original_width": w,
        "original_height": h,
        "aspect_ratio": round(w / max(1, h), 3),
        "steps_applied": []
    }

    # 1. Resizing to standard high-resolution bounding box for OCR
    max_dim = 2000
    min_dim = 800
    scale = 1.0
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
    elif min(h, w) < min_dim and min(h, w) > 0:
        scale = min_dim / min(h, w)

    if scale != 1.0:
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(original, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        metadata["steps_applied"].append(f"Resized ({w}x{h} -> {new_w}x{new_h})")
    else:
        resized = original.copy()

    # 2. Grayscale conversion
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    metadata["steps_applied"].append("Grayscale conversion")

    # 3. Deskewing
    deskew_angle = calculate_skew_angle(gray)
    metadata["skew_angle_detected"] = round(deskew_angle, 2)
    if abs(deskew_angle) > 0.7 and abs(deskew_angle) < 45.0:
        (h_r, w_r) = gray.shape
        center = (w_r // 2, h_r // 2)
        rot_mat = cv2.getRotationMatrix2D(center, deskew_angle, 1.0)
        gray = cv2.warpAffine(gray, rot_mat, (w_r, h_r), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        resized = cv2.warpAffine(resized, rot_mat, (w_r, h_r), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        metadata["steps_applied"].append(f"Deskewed by {deskew_angle:.2f} deg")

    # 4. Contrast enhancement using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)
    metadata["steps_applied"].append("CLAHE contrast enhancement")

    # 5. Mild bilateral filtering to preserve edges while removing high-frequency noise
    denoised = cv2.bilateralFilter(enhanced_gray, d=5, sigmaColor=50, sigmaSpace=50)
    metadata["steps_applied"].append("Bilateral noise filtering")

    # 6. Subtle unsharp mask sharpening
    gaussian = cv2.GaussianBlur(denoised, (0, 0), 2.0)
    sharpened = cv2.addWeighted(denoised, 1.5, gaussian, -0.5, 0)
    metadata["steps_applied"].append("Unsharp mask sharpening")

    # Convert preprocessed gray back to 3-channel for OCR engine
    preprocessed_bgr = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)

    return original, preprocessed_bgr, metadata


def calculate_skew_angle(gray_image: np.ndarray) -> float:
    """Detects primary text orientation angle using minimum area bounding box of text contours."""
    try:
        # Otsu thresholding
        _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # Find coordinates of all foreground pixels
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) < 100:
            return 0.0
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        elif angle > 45:
            angle = 90 - angle
        return float(angle)
    except Exception:
        return 0.0


def extract_text(image_path: str, save_preprocessed: bool = True) -> Dict[str, Any]:
    """
    Performs full OCR text extraction on a food label image.
    Executes OpenCV preprocessing, runs RapidOCR, extracts bounding boxes, text lines,
    confidence metrics, and generates warnings if confidence is low.
    """
    original_bgr, preprocessed_bgr, meta = preprocess_image(image_path)
    ocr = get_ocr_engine()

    # Run OCR on preprocessed image
    results, _ = ocr(preprocessed_bgr)

    # Fallback to original image if preprocessed yields too few lines
    if not results or len(results) < 2:
        orig_results, _ = ocr(original_bgr)
        if orig_results and len(orig_results) > (len(results) if results else 0):
            results = orig_results
            meta["ocr_source"] = "original_image"
        else:
            meta["ocr_source"] = "preprocessed_image"
    else:
        meta["ocr_source"] = "preprocessed_image"

    lines: List[Dict[str, Any]] = []
    text_blocks: List[str] = []
    confidences: List[float] = []

    if results:
        for item in results:
            box, text, conf = item
            clean_text = text.strip()
            if not clean_text:
                continue
            conf_val = float(conf)
            lines.append({
                "text": clean_text,
                "confidence": round(conf_val, 4),
                "box": [[float(pt[0]), float(pt[1])] for pt in box]
            })
            text_blocks.append(clean_text)
            confidences.append(conf_val)

    avg_confidence = round(float(np.mean(confidences)), 4) if confidences else 0.0
    full_text = "\n".join(text_blocks)

    is_low_confidence = avg_confidence < 0.65 or len(lines) == 0
    warnings = []
    if len(lines) == 0:
        warnings.append("No text could be detected from this image. Please provide a clearer or more evenly illuminated photo.")
    elif avg_confidence < 0.65:
        warnings.append(f"OCR confidence is relatively low ({int(avg_confidence * 100)}%). Please review the extracted text and verify key values.")

    # Save preprocessed image preview for user visualization
    preprocessed_path = None
    if save_preprocessed and os.path.exists(image_path):
        dir_name = os.path.dirname(image_path)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        preprocessed_filename = f"{base_name}_preprocessed.jpg"
        preprocessed_path = os.path.join(dir_name, preprocessed_filename)
        cv2.imwrite(preprocessed_path, preprocessed_bgr)

    return {
        "full_text": full_text,
        "line_count": len(lines),
        "lines": lines,
        "average_confidence": avg_confidence,
        "is_low_confidence": is_low_confidence,
        "warnings": warnings,
        "preprocessing": meta,
        "preprocessed_image_path": preprocessed_path
    }
