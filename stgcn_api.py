import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import torch
import json
import os
import mediapipe as mp
from models.stgcn import STGCN  # Import class từ thư mục models

# --------------------
# 1. CẤU HÌNH & LOAD RESOURCES
# --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Đường dẫn các file (Đảm bảo bạn đã copy vào thư mục models)
MODEL_PATH = os.path.join(MODELS_DIR, 'stgcn_best.pth')
GRAPH_PATH = os.path.join(MODELS_DIR, 'mediapipe_graph.npy')
LABEL_PATH = os.path.join(MODELS_DIR, 'label_map.json')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"API running on: {device}")

# --- Load Graph (A) ---
try:
    A = np.load(GRAPH_PATH)
except FileNotFoundError:
    raise RuntimeError("Thiếu file mediapipe_graph.npy trong thư mục models!")

# --- Load Model & Label Map ---
# Vì file .pth mới của bạn chứa cả label_map, ta ưu tiên load từ đó
try:
    checkpoint = torch.load(MODEL_PATH, map_location=device)
    
    # Lấy label map từ checkpoint (nếu có), hoặc load từ file json rời
    if 'label_map' in checkpoint:
        label_map = checkpoint['label_map']
    else:
        with open(LABEL_PATH, 'r', encoding='utf-8') as f:
            label_map = json.load(f)
    
    inv_label_map = {v: k for k, v in label_map.items()}
    
    # Khởi tạo Model (Lưu ý num_class lấy từ label_map)
    model = STGCN(in_channels=3, num_class=len(label_map), A=A)
    
    # Load weights
    if 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model.load_state_dict(checkpoint)
        
    model.to(device)
    model.eval()
    print("✅ Model loaded successfully!")

except Exception as e:
    print(f"❌ Lỗi load model: {e}")
    raise e

# --------------------
# 2. MEDIAPIPE SETUP
# --------------------
mp_holistic = mp.solutions.holistic
# Dùng static_image_mode=True vì API nhận ảnh tĩnh
holistic = mp_holistic.Holistic(
    static_image_mode=True,
    model_complexity=1,
    min_detection_confidence=0.5
)

# --------------------
# 3. HELPER FUNCTIONS
# --------------------
def extract_keypoints(results):
    """Trích xuất và Chuẩn hóa dữ liệu giống hệt lúc train"""
    # Pose (33x3)
    pose = np.array([[lm.x, lm.y, lm.z] for lm in results.pose_landmarks.landmark]).flatten() \
           if results.pose_landmarks else np.zeros(33*3)
    # Left Hand (21x3)
    lh = np.array([[lm.x, lm.y, lm.z] for lm in results.left_hand_landmarks.landmark]).flatten() \
         if results.left_hand_landmarks else np.zeros(21*3)
    # Right Hand (21x3)
    rh = np.array([[lm.x, lm.y, lm.z] for lm in results.right_hand_landmarks.landmark]).flatten() \
         if results.right_hand_landmarks else np.zeros(21*3)

    # Gộp lại (225 điểm)
    kps = np.concatenate([pose, lh, rh]).reshape(-1, 3)

    # --- Normalization (QUAN TRỌNG) ---
    # 1. Center by Hip
    center = kps[0].copy()
    kps -= center

    # 2. Scale by Shoulder
    shoulder_dist = np.linalg.norm(kps[11] - kps[12])
    if shoulder_dist > 0:
        kps /= shoulder_dist

    return kps.flatten()

# --------------------
# 4. PREDICT ROUTE
# --------------------
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Đọc ảnh từ client gửi lên
        data = await file.read()
        nparr = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # MediaPipe xử lý
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(frame_rgb)
        
        # Trích xuất keypoints (75 điểm x 3)
        keypoints = extract_keypoints(results)
        
        # Reshape cho đúng Input Model: (Batch, Channels, Time, Vertices, Person)
        # Với ảnh tĩnh: Time = 1
        # Shape: (1, 3, 1, 75, 1)
        
        # Resize về (1, 75, 3)
        seq_np = keypoints.reshape(1, 75, 3)
        
        # Transpose -> (1, 3, 1, 75)
        seq_input = seq_np.transpose(2, 0, 1) # (3, 1, 75)
        
        # Thêm dimension Batch và Person -> (1, 3, 1, 75, 1)
        seq_input = seq_input[np.newaxis, ..., np.newaxis]
        
        # Chuyển sang Tensor
        x = torch.FloatTensor(seq_input).to(device)
        
        # Dự đoán
        with torch.no_grad():
            out = model(x)
            prob = torch.softmax(out, dim=1)
            pred_idx = prob.argmax(dim=1).item()
            confidence = prob[0, pred_idx].item()
            
            pred_label = inv_label_map[pred_idx]

        return {
            "success": True,
            "label": pred_label,
            "confidence": float(confidence)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)