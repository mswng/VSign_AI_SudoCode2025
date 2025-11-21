# stgcn_api.py
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import torch
from models.stgcn import STGCN
import mediapipe as mp

# --------------------
# FastAPI setup
# --------------------
app = FastAPI()

# allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# --------------------
# Load STGCN model
# --------------------
num_class = 110       # Số class thực tế của model
num_point = 33        # Pose 33 keypoints
in_channels = 3

# adjacency matrix A (nên dùng A giống khi train)
A = np.eye(num_point, dtype=np.float32)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = STGCN(in_channels=in_channels, num_class=num_class, A=A)
model.load_state_dict(torch.load("models/stgcn_best.pth", map_location=device))
model.eval()
model.to(device)

# --------------------
# Label map
# --------------------
# nếu model có 110 class, tạo label tạm thời để test
LABELS = [f"class_{i}" for i in range(num_class)]
# bạn có thể thay bằng ["xin_chao", "cam_on", ...] nếu đúng số lớp

# --------------------
# Predict route
# --------------------
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Đọc ảnh
    data = await file.read()
    nparr = np.frombuffer(data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # --------------------
    # Extract skeleton with Mediapipe
    # --------------------
    mp_holistic = mp.solutions.holistic
    with mp_holistic.Holistic(static_image_mode=True) as holistic:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(frame_rgb)

    skeleton = []
    if results.pose_landmarks:
        for lm in results.pose_landmarks.landmark:
            skeleton.extend([lm.x, lm.y, lm.z])
    else:
        # Nếu không detect được, fill 0
        skeleton = [0.0] * (num_point * 3)

    # --------------------
    # Convert to tensor (N, C, T, V)
    # --------------------
    x = np.array(skeleton, dtype=np.float32).reshape(1, 3, 1, num_point)
    x = torch.tensor(x, dtype=torch.float32).to(device)

    # --------------------
    # Model inference
    # --------------------
    with torch.no_grad():
        out = model(x)                  # shape (1, num_class)
        prob = torch.softmax(out, dim=1)
        pred_idx = prob.argmax(dim=1).item()
        confidence = prob[0, pred_idx].item()
        # safety check
        if pred_idx >= len(LABELS):
            pred_label = "unknown"
        else:
            pred_label = LABELS[pred_idx]

    return {"label": pred_label, "confidence": confidence}
