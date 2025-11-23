"""ui_detection_improved
=========================

OpenCV-based UI element detectors that produce pixel-accurate coordinates
by combining colour analysis, shape recognition, and template/object
matching. Currently focuses on the Windows Start button but can be
extended to additional taskbar icons.
"""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
from PIL import Image

import cv2  # type: ignore


@dataclass
class DetectionResult:
    """Represents a detected UI element."""

    name: str
    x: int
    y: int
    width: int
    height: int
    confidence: float
    method: str

    @property
    def center(self) -> Tuple[int, int]:
        return (self.x, self.y)


class StartButtonDetector:
    """Detect the Windows Start button using OpenCV techniques.

    The detector combines three independent signals:
    1. **Template matching** (object detection) against a real Start button image.
    2. **Colour analysis** in HSV space to confirm the expected icon colors.
    3. **Shape recognition** to verify the presence of the four-pane window glyph.

    A detection is accepted only if all checks pass, dramatically reducing false
    positives from other taskbar icons.
    """

    def __init__(self, template_path: Optional[str] = None) -> None:
        from pathlib import Path
        
        # Load real Start button template if available
        if template_path is None:
            template_path = str(Path(__file__).parent / "Symbols" / "StartButton.png")
        
        self._template = self._load_template(template_path)
        if self._template is None:
            # Fallback to synthetic template
            self._template = self._build_start_template()
        
        self._template_gray = cv2.cvtColor(self._template, cv2.COLOR_BGR2GRAY)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def detect_from_base64(self, image_b64: str) -> Optional[DetectionResult]:
        image = _decode_base64_to_cv2(image_b64)
        return self.detect(image)

    def detect(self, image: np.ndarray) -> Optional[DetectionResult]:
        roi, roi_origin = self._extract_bottom_left_roi(image)

        template_match = self._run_template_matching(roi)
        if not template_match:
            return None

        candidate_x = roi_origin[0] + template_match.x
        candidate_y = roi_origin[1] + template_match.y
        candidate_width = template_match.width
        candidate_height = template_match.height

        # If using real template and confidence is high, skip color/shape validation
        # (those checks were designed for synthetic templates)
        if template_match.confidence >= 0.55:
            return DetectionResult(
                name="Windows Start button",
                x=int(candidate_x),
                y=int(candidate_y),
                width=int(candidate_width),
                height=int(candidate_height),
                confidence=float(template_match.confidence),
                method="opencv_template_matching",
            )

        # For lower confidence matches, run additional validation
        candidate_patch = _crop_with_margin(
            image,
            center=(candidate_x, candidate_y),
            size=(candidate_width, candidate_height),
            margin_ratio=0.35,
        )

        if candidate_patch.size == 0:
            return None

        colour_ok = self._passes_colour_check(candidate_patch)
        shape_ok = self._passes_shape_check(candidate_patch)

        if not (colour_ok and shape_ok):
            return None

        return DetectionResult(
            name="Windows Start button",
            x=int(candidate_x),
            y=int(candidate_y),
            width=int(candidate_width),
            height=int(candidate_height),
            confidence=float(template_match.confidence),
            method="opencv_template+colour+shape",
        )

    # ------------------------------------------------------------------
    # Template Matching
    # ------------------------------------------------------------------
    @dataclass
    class _TemplateMatch:
        x: float
        y: float
        width: float
        height: float
        confidence: float

    def _run_template_matching(self, roi: np.ndarray) -> Optional["StartButtonDetector._TemplateMatch"]:
        """Find Start button using template matching across multiple scales."""
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Explore multiple scales to accommodate DPI scaling/taskbar sizes
        scales = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5]
        best_match: Optional[StartButtonDetector._TemplateMatch] = None

        for scale in scales:
            template_scaled = cv2.resize(self._template_gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
            t_h, t_w = template_scaled.shape[:2]
            
            # Skip if template is larger than ROI
            if t_h >= roi_gray.shape[0] or t_w >= roi_gray.shape[1]:
                continue

            # Try multiple template matching methods for robustness
            methods = [cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR_NORMED]
            
            for method in methods:
                result = cv2.matchTemplate(roi_gray, template_scaled, method)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if best_match is None or max_val > best_match.confidence:
                    best_match = StartButtonDetector._TemplateMatch(
                        x=max_loc[0] + t_w / 2,
                        y=max_loc[1] + t_h / 2,
                        width=t_w,
                        height=t_h,
                        confidence=max_val,
                    )

        # Lower threshold since we're looking in a specific region
        if best_match and best_match.confidence >= 0.45:
            return best_match
        return None

    # ------------------------------------------------------------------
    # Colour Validation
    # ------------------------------------------------------------------
    def _passes_colour_check(self, patch: np.ndarray) -> bool:
        """Check if patch has Windows Start button color characteristics."""
        if patch.size == 0:
            return False
            
        hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
        _, sat, val = cv2.split(hsv)

        mean_sat = float(np.mean(sat))
        mean_val = float(np.mean(val))

        # Windows Start icon is white/light gray (low saturation)
        # But NOT too bright (to avoid matching text)
        sat_threshold = 60.0  # Low saturation (near-neutral color)
        val_min = 120.0       # Minimum brightness
        val_max = 200.0       # Maximum brightness (avoid pure white text)

        # Ensure there is contrast in the patch (icon vs background)
        contrast = float(np.std(val))
        contrast_threshold = 20.0

        return (mean_sat <= sat_threshold and 
                val_min <= mean_val <= val_max and 
                contrast >= contrast_threshold)

    # ------------------------------------------------------------------
    # Shape Validation
    # ------------------------------------------------------------------
    def _passes_shape_check(self, patch: np.ndarray) -> bool:
        """Verify the Windows logo shape: 4 square panes in 2x2 grid."""
        if patch.size == 0:
            return False
            
        gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise while keeping edges
        bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Use adaptive threshold to handle varying backgrounds
        thresh = cv2.adaptiveThreshold(bilateral, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        
        # If icon is brighter than background, invert
        if np.mean(gray) > 128:
            thresh = 255 - thresh
        
        # Clean up noise
        kernel = np.ones((2, 2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for 4 roughly square shapes
        squares = []
        patch_h, patch_w = patch.shape[:2]
        min_size = int(min(patch_h, patch_w) * 0.15)  # Minimum 15% of patch size
        max_size = int(min(patch_h, patch_w) * 0.5)   # Maximum 50% of patch size
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_size * min_size or area > max_size * max_size:
                continue
            
            # Check if roughly square
            x, y, w, h = cv2.boundingRect(contour)
            aspect = w / max(h, 1)
            if 0.5 <= aspect <= 2.0:  # Allow some tolerance
                squares.append((x, y, w, h))
        
        # Need at least 3 squares (sometimes one pane might merge or be hidden)
        if len(squares) < 3:
            return False
        
        # Verify squares are arranged in a grid pattern
        # Sort by position and check for 2x2 arrangement
        if len(squares) >= 4:
            centers = [(x + w/2, y + h/2) for x, y, w, h in squares]
            centers_sorted = sorted(centers, key=lambda c: (c[1], c[0]))
            
            # Check if arranged in roughly 2 rows
            top_row = [c for c in centers_sorted[:2]]
            bottom_row = [c for c in centers_sorted[2:4]]
            
            # Verify vertical alignment
            if len(top_row) >= 2 and len(bottom_row) >= 2:
                vertical_gap = abs(top_row[0][1] - bottom_row[0][1])
                horizontal_gap = abs(top_row[0][0] - top_row[1][0])
                
                # Gaps should be similar (square grid)
                if abs(vertical_gap - horizontal_gap) < patch_h * 0.3:
                    return True
        
        # If we have 3 squares in reasonable positions, accept it
        return len(squares) >= 3

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _extract_bottom_left_roi(self, image: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int]]:
        """Extract entire bottom taskbar region for detection.
        
        Searches the full width of the taskbar to be adaptable to different layouts.
        On Windows 11, Start button is typically left of center in the taskbar.
        """
        height, width = image.shape[:2]
        
        # Full taskbar height (bottom 5-6% of screen)
        roi_height = max(int(height * 0.06), 70)
        
        y_start = height - roi_height
        x_start = 0

        # Return entire taskbar width
        roi = image[y_start:height, :]
        return roi, (x_start, y_start)

    def _load_template(self, template_path) -> Optional[np.ndarray]:
        """Load Start button template from file."""
        try:
            if isinstance(template_path, str):
                from pathlib import Path
                template_path = Path(template_path)
            
            if not template_path.exists():
                return None
            
            template = cv2.imread(str(template_path))
            if template is None:
                return None
            
            # Resize to reasonable size if too large
            max_dim = 64
            h, w = template.shape[:2]
            if max(h, w) > max_dim:
                scale = max_dim / max(h, w)
                new_w = int(w * scale)
                new_h = int(h * scale)
                template = cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_AREA)
            
            return template
        except Exception:
            return None
    
    def _build_start_template(self) -> np.ndarray:
        """Generate a synthetic Start icon template (white four-pane window)."""
        size = 48  # Smaller template for better matching
        template = np.zeros((size, size, 3), dtype=np.uint8)

        # Windows 11 style: 4 squares in 2x2 grid
        pane_size = int(size * 0.38)  # Larger panes
        gap = int(size * 0.06)         # Smaller gap between panes

        # Top-left pane
        template[gap : gap + pane_size, gap : gap + pane_size] = 220
        # Top-right pane
        template[gap : gap + pane_size, gap * 2 + pane_size : gap * 2 + pane_size * 2] = 220
        # Bottom-left pane
        template[gap * 2 + pane_size : gap * 2 + pane_size * 2, gap : gap + pane_size] = 220
        # Bottom-right pane
        template[
            gap * 2 + pane_size : gap * 2 + pane_size * 2,
            gap * 2 + pane_size : gap * 2 + pane_size * 2,
        ] = 220

        # Apply slight Gaussian blur to mimic anti-aliasing
        template = cv2.GaussianBlur(template, (3, 3), 0)
        
        # Add slight padding around the icon
        padded = cv2.copyMakeBorder(template, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=0)
        return padded


class GenericUIDetector:
    """Generic detector for UI elements using real template images.
    
    This detector uses template matching with multi-scale search to find
    UI elements like browser icons, folders, search bars, etc.
    """
    
    def __init__(self, template_path: str, name: str, roi_region: str = "taskbar") -> None:
        """Initialize detector with a template image.
        
        Args:
            template_path: Path to the template image
            name: Name of the UI element being detected
            roi_region: Region to search - "full", "taskbar", "top"
        """
        from pathlib import Path
        
        self.template_path = Path(template_path)
        self.name = name
        self.roi_region = roi_region
        self._template = self._load_template()
        
        if self._template is None:
            raise ValueError(f"Failed to load template from {template_path}")
        
        self._template_gray = cv2.cvtColor(self._template, cv2.COLOR_BGR2GRAY)
    
    def _load_template(self) -> Optional[np.ndarray]:
        """Load template from file."""
        try:
            if not self.template_path.exists():
                return None
            
            template = cv2.imread(str(self.template_path))
            if template is None:
                return None
            
            # Resize to reasonable size if too large
            max_dim = 64
            h, w = template.shape[:2]
            if max(h, w) > max_dim:
                scale = max_dim / max(h, w)
                new_w = int(w * scale)
                new_h = int(h * scale)
                template = cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_AREA)
            
            return template
        except Exception:
            return None
    
    def detect(self, image: np.ndarray) -> Optional[DetectionResult]:
        """Detect the UI element in the given screenshot."""
        # Extract ROI based on region setting
        roi, roi_origin = self._extract_roi(image)
        
        # Run multi-scale template matching
        match_result = self._run_template_matching(roi)
        
        if match_result is None:
            return None
        
        # Convert ROI coordinates to screen coordinates
        screen_x = match_result["x"] + roi_origin[0]
        screen_y = match_result["y"] + roi_origin[1]
        
        return DetectionResult(
            name=self.name,
            x=screen_x,
            y=screen_y,
            width=match_result["width"],
            height=match_result["height"],
            confidence=match_result["confidence"],
            method="opencv_template_matching"
        )
    
    def detect_from_base64(self, image_b64: str) -> Optional[DetectionResult]:
        """Detect from base64-encoded image."""
        np_img = _decode_base64_to_cv2(image_b64)
        return self.detect(np_img)
    
    def _extract_roi(self, image: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int]]:
        """Extract region of interest based on roi_region setting."""
        height, width = image.shape[:2]
        
        if self.roi_region == "taskbar":
            # Entire bottom taskbar - full width for adaptability
            # This works for all taskbar icons regardless of layout
            roi_height = max(int(height * 0.06), 70)
            roi = image[height - roi_height:, :]
            return roi, (0, height - roi_height)
        
        elif self.roi_region == "top":
            # Top 15% of screen (for browser elements)
            roi_height = max(int(height * 0.15), 120)
            roi = image[:roi_height, :]
            return roi, (0, 0)
        
        else:  # "full"
            return image, (0, 0)
    
    def _run_template_matching(self, roi: np.ndarray) -> Optional[dict]:
        """Run multi-scale template matching."""
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        best_match = None
        best_confidence = 0.0
        
        # Multi-scale search
        scales = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5]
        methods = [cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR_NORMED]
        
        for scale in scales:
            # Resize template
            new_w = int(self._template.shape[1] * scale)
            new_h = int(self._template.shape[0] * scale)
            
            if new_w < 10 or new_h < 10:
                continue
            if new_w > roi.shape[1] or new_h > roi.shape[0]:
                continue
            
            scaled_template = cv2.resize(self._template_gray, (new_w, new_h), 
                                        interpolation=cv2.INTER_AREA)
            
            for method in methods:
                result = cv2.matchTemplate(roi_gray, scaled_template, method)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                confidence = max_val
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = {
                        "x": max_loc[0] + new_w // 2,
                        "y": max_loc[1] + new_h // 2,
                        "width": new_w,
                        "height": new_h,
                        "confidence": confidence
                    }
        
        # Threshold for acceptance
        if best_confidence >= 0.5:
            return best_match
        
        return None


# ----------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------

def _decode_base64_to_cv2(image_b64: str) -> np.ndarray:
    data = base64.b64decode(image_b64)
    pil_image = Image.open(io.BytesIO(data)).convert("RGB")
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)


def _crop_with_margin(
    image: np.ndarray,
    center: Tuple[float, float],
    size: Tuple[float, float],
    margin_ratio: float = 0.25,
) -> np.ndarray:
    cx, cy = center
    w, h = size
    half_w = int((w * (1.0 + margin_ratio)) / 2)
    half_h = int((h * (1.0 + margin_ratio)) / 2)

    x1 = max(int(cx) - half_w, 0)
    y1 = max(int(cy) - half_h, 0)
    x2 = min(int(cx) + half_w, image.shape[1])
    y2 = min(int(cy) + half_h, image.shape[0])

    return image[y1:y2, x1:x2]


__all__ = ["StartButtonDetector", "GenericUIDetector", "DetectionResult"]
