"""Check SearchTaskBar template"""
import cv2
from pathlib import Path

for name in ["SearchBar.png", "SearchTaskBar.png"]:
    template_path = Path(f"Symbols/{name}")
    if template_path.exists():
        template = cv2.imread(str(template_path))
        print(f"{name}: {template.shape}")
