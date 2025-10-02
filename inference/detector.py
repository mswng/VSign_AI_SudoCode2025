from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path

# Load mô hình đã train
MODEL_PATH = Path(__file__).resolve().parents[1] / "practice" / "VSL_models" / "best.pt"
model = YOLO(str(MODEL_PATH))
# Chạy nhận diện bằng webcam (source=0)
results = model.predict(source=0, conf=0.25, show=True)
