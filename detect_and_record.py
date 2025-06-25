import cv2
import time
import os
import requests
import threading
from datetime import datetime

# ========== CONFIG ==========
RECORD_DURATION = 15  # seconds
webhook_url = "https://discord.com/api/webhooks/XXXXXXXX"  # replace with your Discord webhook

# ========== SETUP ==========
os.makedirs("videos", exist_ok=True)

# Initialize flags and variables
video_is_recording = False
record_start_time = 0
out = None
video_filename = ""

# Load model
prototxt = "MobileNetSSD_deploy.prototxt"
model = "MobileNetSSD_deploy.caffemodel"
net = cv2.dnn.readNetFromCaffe(prototxt, model)

# Define the class labels MobileNet SSD was trained on
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

# Start video capture
cap = cv2.VideoCapture(0)

# ========== DISCORD FUNCTION ==========
def send_video_to_discord(video_path, webhook_url):
    try:
        with open(video_path, 'rb') as f:
            files = {'file': (os.path.basename(video_path), f)}
            data = {'content': '🎥 Motion detected — here is the clip!'}
            response = requests.post(webhook_url, data=data, files=files)
            if response.ok:
                print("[✅] Video sent to Discord!")
            else:
                print(f"[❌] Failed to send video: {response.status_code}")
    except Exception as e:
        print(f"[❌] Error while sending video: {e}")

# ========== VIDEO CONVERSION ==========
def convert_avi_to_mp4(avi_path):
    mp4_path = avi_path.replace(".avi", ".mp4")
    os.system(f"ffmpeg -y -i \"{avi_path}\" -vcodec libx264 \"{mp4_path}\"")
    os.remove(avi_path)  # optional: delete original AVI to save space
    return mp4_path

# ========== MAIN LOOP ==========
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Prepare image for detection
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    person_detected = False

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            idx = int(detections[0, 0, i, 1])
            if idx < len(CLASSES):
                label = CLASSES[idx]
                if label == "person":
                    person_detected = True
                    box = detections[0, 0, i, 3:7] * [frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]]
                    (startX, startY, endX, endY) = box.astype("int")
                    cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                    text = f"{label}: {confidence:.2f}"
                    cv2.putText(frame, text, (startX, startY - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Start recording if a person is detected and not already recording
    current_time = time.time()
    if person_detected and not video_is_recording:
        video_is_recording = True
        record_start_time = current_time
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        video_filename = f"videos/person_{timestamp}.avi"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(video_filename, fourcc, 10.0, (frame.shape[1], frame.shape[0]))
        print(f"[🎥] Started recording: {video_filename}")

    # Continue writing to video if recording
    if video_is_recording:
        out.write(frame)
        if current_time - record_start_time >= RECORD_DURATION:
            out.release()
            video_is_recording = False
            print(f"[✅] Finished recording: {video_filename}")

            # Convert to MP4
            mp4_filename = convert_avi_to_mp4(video_filename)
            print(f"[🎞️] Converted to MP4: {mp4_filename}")

            # Send MP4 to Discord in background
            threading.Thread(target=send_video_to_discord, args=(mp4_filename, webhook_url)).start()

    # (Optional) Display the frame locally
    # cv2.imshow("Frame", frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# Cleanup
cap.release()
cv2.destroyAllWindows()
