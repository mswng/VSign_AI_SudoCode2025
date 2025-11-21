# stgcn_api.py
import io
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import torch
from models.stgcn import STGCN  # file class STGCN của bạn

app = FastAPI()

# allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # hoặc địa chỉ frontend của bạn
    allow_methods=["*"],
    allow_headers=["*"]
)

# Load model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = STGCN(...)  # init architecture
model.load_state_dict(torch.load("models/stgcn_best.pth", map_location=device))
model.eval()
model.to(device)

# Map label idx -> label name
LABELS = ["xin_chao", "cam_on", "toi", "ban", "..."]  # điền đầy đủ label bạn train

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # đọc ảnh từ frontend
    data = await file.read()
    nparr = np.frombuffer(data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Extract skeleton keypoints với Mediapipe
    import mediapipe as mp
    mp_holistic = mp.solutions.holistic
    with mp_holistic.Holistic(static_image_mode=True) as holistic:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(frame_rgb)
    
    # Chuyển keypoints thành input tensor ST-GCN
    skeleton = []
    if results.pose_landmarks:
        for lm in results.pose_landmarks.landmark:
            skeleton.extend([lm.x, lm.y, lm.z])
    else:
        skeleton = [0.0] * (33*3)  # 33 keypoints * 3

    # reshape input (1, C, T, V) -> giả sử T=1, C=3, V=33
    x = np.array(skeleton, dtype=np.float32).reshape(1, 3, 1, 33)
    x = torch.tensor(x, dtype=torch.float32).to(device)

    with torch.no_grad():
        out = model(x)
        pred_idx = out.argmax(dim=1).item()
        pred_label = LABELS[pred_idx]

    return {"label": pred_label}
