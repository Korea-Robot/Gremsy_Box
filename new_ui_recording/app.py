

from flask import Flask, render_template, request, jsonify
import requests
import os
import logging


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 환경변수에서 API 포트 가져오기 (기본값: 6783)
API_PORT = int(os.environ.get('API_PORT', 6783))

@app.route('/')
def index():
    # 클라이언트의 요청 호스트에서 IP만 추출해서 동적 webrtc 할당
    client_host = request.host.split(':')[0]
    mediamtx_url = f"http://{client_host}:8889/eo-ir-vio/"
    # 콘솔 디버깅용 로그 출력
    print(f"🔍 client_host: {client_host}")
    print(f"🔗 mediamtx_url: {mediamtx_url}")
    return render_template(
        'index.html',
        webrtc_url=mediamtx_url,
        rtsp_url  ="192.168.168.240:554/payload",
        robot_ip=client_host
    )

@app.route('/api/camera/<action>', methods=['POST'])
def camera_control(action):
    try:
        client_host = "127.0.0.1"
        data = request.json
        
        # API 엔드포인트 매핑
        endpoints = {
            'zoom-step': f"http://{client_host}:{API_PORT}/camera/zoom/step",
            'zoom-continuous': f"http://{client_host}:{API_PORT}/camera/zoom/continuous",
            'zoom-range': f"http://{client_host}:{API_PORT}/camera/zoom/range",
            'change-view': f"http://{client_host}:{API_PORT}/camera/change-view-src",
            'focus-mode': f"http://{client_host}:{API_PORT}/camera/focus/set-mode",
            'focus-continuous': f"http://{client_host}:{API_PORT}/camera/focus/continuous",
            'focus-auto': f"http://{client_host}:{API_PORT}/camera/focus/auto",
            'ir-palette': f"http://{client_host}:{API_PORT}/camera/set-ir-palette",
            'osd-mode': f"http://{client_host}:6783/camera/set-osd-mode",
            'flip-mode': f"http://{client_host}:{API_PORT}/camera/set-flip-mode"
        }
        
        if action not in endpoints:
            return jsonify({'error': 'Invalid action'}), 400
            
        url = endpoints[action]
        
        if action == 'focus-auto':
            response = requests.post(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
            
        return jsonify({'status': 'success', 'response': response.status_code})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gimbal/<action>', methods=['POST'])
def gimbal_control(action):
    try:
        client_host = "127.0.0.1"
        data = request.json
        
        endpoints = {
            'set-mode': f"http://{client_host}:{API_PORT}/gimbal/set-mode",
            'position-move': f"http://{client_host}:{API_PORT}/gimbal/positionMove",
            'move': f"http://{client_host}:{API_PORT}/gimbal/move"
        }
        
        if action not in endpoints:
            return jsonify({'error': 'Invalid action'}), 400
            
        url = endpoints[action]
        response = requests.post(url, json=data, timeout=5)
        
        return jsonify({'status': 'success', 'response': response.status_code})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500







import threading          # 녹화 작업을 백그라운드 스레드에서 실행하기 위해 사용
import cv2                # OpenCV 라이브러리 (RTSP 스트림 열기 및 비디오 저장)
from datetime import datetime  # 저장 파일에 타임스탬프를 부여하기 위해 사용
import os
from flask import request, jsonify  # Flask의 HTTP 요청 핸들링을 위해 import


# RTSP 스트림 녹화 함수
def record_rtsp_stream(rtsp_url, output_path):
    global recording_flag

    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print(f"⚠️ Failed to open RTSP stream: {rtsp_url}")
        return

    # 프레임 크기 설정 (선택사항)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # 실제 프레임 크기 확인
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 20
    
    print(f"📹 Recording settings: {width}x{height} @ {fps}fps")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # mp4v 코덱 사용
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recording_{timestamp}.mp4"
    filepath = os.path.join(output_path, filename)
    
    out = cv2.VideoWriter(filepath, fourcc, fps, (width, height))

    frame_count = 0
    while recording_flag and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Failed to read frame from RTSP stream")
            break
        
        out.write(frame)
        frame_count += 1
        
        if frame_count % (fps * 10) == 0:  # 10초마다 로그 출력
            print(f"📹 Recording... {frame_count // fps}초 경과")

    cap.release()
    out.release()
    print(f"✅ Recording saved: {filepath} ({frame_count} frames)")

@app.route('/api/camera/rtsp_video_recording', methods=['POST'])
def rtsp_recording():
    global recording_flag, recording_thread

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    action = data.get("action")
    rtsp_url = data.get("rtsp_url")
    output_path = data.get("output_path", "/app/data/recordings")  # Docker 볼륨 마운트 경로
    
    # 저장 디렉토리 생성
    try:
        os.makedirs(output_path, exist_ok=True)
        print(f"📁 Recording directory: {output_path}")
    except Exception as e:
        return jsonify({"error": f"Failed to create directory: {str(e)}"}), 500

    if action == "start":
        if recording_flag:
            return jsonify({"status": "already recording"}), 400
        
        if not rtsp_url:
            return jsonify({"error": "rtsp_url is required"}), 400
            
        print(f"🎬 Starting recording from: {rtsp_url}")
        recording_flag = True
        recording_thread = threading.Thread(
            target=record_rtsp_stream,
            args=(rtsp_url, output_path),
            daemon=True
        )
        recording_thread.start()
        return jsonify({"status": "recording started", "rtsp_url": rtsp_url, "output_path": output_path}), 200

    elif action == "stop":
        if not recording_flag:
            return jsonify({"status": "not currently recording"}), 400
        
        print("⏹️ Stopping recording...")
        recording_flag = False
        if recording_thread and recording_thread.is_alive():
            recording_thread.join(timeout=10)
        return jsonify({"status": "recording stopped"}), 200

    return jsonify({"error": "Invalid action. Use 'start' or 'stop'"}), 400

@app.route('/api/camera/capture_image', methods=['POST'])
def capture_image():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        rtsp_url = data.get("rtsp_url")
        output_path = data.get("output_path", "/app/data/captures")  # Docker 볼륨 마운트 경로
        
        if not rtsp_url:
            return jsonify({"error": "rtsp_url is required"}), 400

        # 저장 디렉토리 생성
        os.makedirs(output_path, exist_ok=True)
        print(f"📁 Capture directory: {output_path}")

        # RTSP 스트림에서 프레임 캡처
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            return jsonify({"error": f"Failed to open RTSP stream: {rtsp_url}"}), 500

        ret, frame = cap.read()
        cap.release()

        if not ret:
            return jsonify({"error": "Failed to capture frame from stream"}), 500

        # 이미지 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.jpg"
        filepath = os.path.join(output_path, filename)
        
        success = cv2.imwrite(filepath, frame)
        if not success:
            return jsonify({"error": "Failed to save image"}), 500

        print(f"📸 Image captured: {filepath}")
        return jsonify({
            "status": "image captured", 
            "file_path": filepath,
            "filename": filename,
            "rtsp_url": rtsp_url
        }), 200

    except Exception as e:
        print(f"❌ Capture error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/camera/recording_status', methods=['GET'])
def recording_status():
    """녹화 상태 확인"""
    return jsonify({
        "is_recording": recording_flag,
        "thread_alive": recording_thread.is_alive() if recording_thread else False
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 7778))
    print(f"🚀 Starting Flask app on port {port}")
    print(f"🔧 API calls will be made to port {API_PORT}")
    print(f"📁 Data directory: /app/data")
    
    # 데이터 디렉토리 생성
    os.makedirs("/app/data/recordings", exist_ok=True)
    os.makedirs("/app/data/captures", exist_ok=True)
    
    app.run(host="0.0.0.0", port=port, debug=True)