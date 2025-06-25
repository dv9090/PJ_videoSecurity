# PJ_videoSecurity

📂 Project: Home Security System with Object Detection
Real-time person detection, video recording, and alerting system for Raspberry Pi using OpenCV and Discord webhooks.

* 📸 Features
  *  ✅ Real-time person detection using MobileNet SSD
  * 🎥 Automatically records 15-second video clips

  -🔄 Converts .avi to .mp4 for better compatibility

  -📤 Sends video alerts to a Discord channel via webhook

  -🧠 Optimized to run on low-resource hardware (Raspberry Pi)

  -🔁 Uses Python threading to upload without blocking detection

🛠️ Technologies Used
Python

OpenCV

MobileNet SSD

ffmpeg (via system call)

Discord Webhooks

Raspberry Pi OS (tested on Pi 4)

🚀 How It Works
Motion is detected in the frame

A person is identified using MobileNet SSD

A 15-second video clip is recorded

Video is converted to .mp4 format

The clip is sent to a Discord channel using a webhook

System continues to monitor in real time
