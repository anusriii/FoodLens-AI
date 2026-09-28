import os
import cv2
import numpy as np
import pytest
from app.ocr import preprocess_image, extract_text

def test_preprocess_synthetic_image(tmp_path):
    # Create synthetic test label image
    img = np.ones((400, 800, 3), dtype=np.uint8) * 255
    cv2.putText(img, "FOOD LABEL TEST", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    test_img_path = str(tmp_path / "test_label.png")
    cv2.imwrite(test_img_path, img)

    orig, prep, meta = preprocess_image(test_img_path)
    assert orig is not None
    assert prep is not None
    assert "original_width" in meta
    assert len(meta["steps_applied"]) > 0

def test_ocr_extraction(tmp_path):
    img = np.ones((300, 900, 3), dtype=np.uint8) * 255
    cv2.putText(img, "INGREDIENTS: Wheat flour, Sugar", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(img, "Energy: 450 kcal", (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    test_img_path = str(tmp_path / "test_ocr.png")
    cv2.imwrite(test_img_path, img)

    result = extract_text(test_img_path, save_preprocessed=False)
    assert "full_text" in result
    assert result["line_count"] > 0
    assert result["average_confidence"] > 0.0
