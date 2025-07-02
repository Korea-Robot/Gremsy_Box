
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




##################################################
##########    RTSP Capture Record       ##########
##################################################

import threading          # 녹화 작업을 백그라운드 스레드에서 실행하기 위해 사용
import cv2                # OpenCV 라이브러리 (RTSP 스트림 열기 및 비디오 저장)
from datetime import datetime  # 저장 파일에 타임스탬프를 부여하기 위해 사용
import os
from flask import request, jsonify  # Flask의 HTTP 요청 핸들링을 위해 import

# Flask route 밖에서 사용할 전역 변수들
recording_thread = None     # 녹화용 스레드 핸들러
recording_flag = False      # 현재 녹화 중인지 여부를 나타내는 플래그

"""
# RTSP 스트림을 열고 비디오로 저장하는 함수 (백그라운드 스레드에서 실행됨)
def record_rtsp_stream(rtsp_url, output_path):
    global recording_flag
    
    # RTSP 스트림 열기
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print("⚠️ Failed to open RTSP stream.")
        return

    # 비디오 저장용 코덱 설정 (XVID는 .avi 포맷에 적합)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    # 파일 이름에 사용할 현재 시간 타임스탬프 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 비디오 저장 객체 생성 (해상도는 640x480, fps는 20)
    out = cv2.VideoWriter(f"{output_path}/recording_{timestamp}.avi", fourcc, 20.0, (640, 480))

    # 스트림에서 프레임을 계속 읽어와 저장
    while recording_flag and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            out.write(frame)  # 프레임 저장
        else:
            break  # 스트림 문제가 생기면 루프 종료

    # 녹화 종료 시 리소스 정리
    cap.release()
    out.release()

# Flask API 엔드포인트: RTSP 비디오 녹화 제어 (시작/종료)
@app.route('/api/camera/rtsp_video_recording', methods=['POST'])
def rtsp_recording():
    global recording_flag, recording_thread

    # 📌 request.json은 클라이언트가 보낸 POST 요청의 JSON 바디를 읽는 부분입니다.
    # 예: { "action": "start", "rtsp_url": "...", "output_path": "..." }
    data = request.json

    # JSON에서 액션 종류("start" 또는 "stop")와 스트림 URL, 저장 경로 추출
    action = data.get("action")
    rtsp_url = data.get("rtsp_url")
    output_path = data.get("output_path", "./recordings")  # 경로가 없으면 기본값

    # 녹화 시작 요청 처리
    if action == "start":
        if not recording_flag:
            # 녹화 시작 상태로 전환
            recording_flag = True

            # 저장 디렉토리 없으면 생성
            os.makedirs(output_path, exist_ok=True)

            # 백그라운드에서 녹화 수행
            recording_thread = threading.Thread(
                target=record_rtsp_stream,
                args=(rtsp_url, output_path)
            )
            recording_thread.start()

            return jsonify({"status": "recording started"}), 200
        else:
            return jsonify({"status": "already recording"}), 400  # 중복 시작 방지

    # 녹화 중지 요청 처리
    elif action == "stop":
        if recording_flag:
            recording_flag = False  # 루프 종료를 위한 플래그 변경
            recording_thread.join()  # 백그라운드 스레드 종료 대기
            return jsonify({"status": "recording stopped"}), 200
        else:
            return jsonify({"status": "not currently recording"}), 400  # 중지 시도시 에러

    # action이 "start" 또는 "stop"이 아닌 경우
    return jsonify({"error": "Invalid action"}), 400

    # request.json: 클라이언트에서 POST로 보낸 JSON 데이터를 읽는 부분입니다.


    
@app.route('/api/camera/capture_image', methods=['POST'])
def capture_image():
    try:
        data = request.json
        rtsp_url = data.get("rtsp_url")
        output_path = data.get("output_path", "./captures")

        # 저장 폴더 생성
        os.makedirs(output_path, exist_ok=True)

        # 스트림 열기
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            return jsonify({"error": "Failed to open RTSP stream"}), 500

        ret, frame = cap.read()
        cap.release()

        if not ret:
            return jsonify({"error": "Failed to capture frame"}), 500

        # 저장 경로 및 파일 이름 설정
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(output_path, f"capture_{timestamp}.jpg")
        cv2.imwrite(file_path, frame)

        return jsonify({"status": "image captured", "file_path": file_path}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""



def record_rtsp_stream(rtsp_url, output_path):
    global recording_flag

    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print("⚠️ Failed to open RTSP stream.")
        return

    # optional: enforce frame size
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(output_path, f"recording_{timestamp}.avi")
    out = cv2.VideoWriter(filepath, fourcc, 20.0, (640, 480))

    while recording_flag and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()
    print(f"▶️ Recording saved to {filepath}")

@app.route('/api/camera/rtsp_video_recording', methods=['POST'])
def rtsp_recording():
    global recording_flag, recording_thread

    data = request.get_json()
    action = data.get("action")
    rtsp_url = data.get("rtsp_url")
    output_path = data.get("output_path", "./recordings")
    os.makedirs(output_path, exist_ok=True)

    if action == "start":
        if recording_flag:
            return jsonify({"status": "already recording"}), 400
        recording_flag = True
        recording_thread = threading.Thread(
            target=record_rtsp_stream,
            args=(rtsp_url, output_path),
            daemon=True
        )
        recording_thread.start()
        return jsonify({"status": "recording started"}), 200

    elif action == "stop":
        if not recording_flag:
            return jsonify({"status": "not currently recording"}), 400
        recording_flag = False
        recording_thread.join(timeout=5)
        return jsonify({"status": "recording stopped"}), 200

    return jsonify({"error": "Invalid action"}), 400

@app.route('/api/camera/capture_image', methods=['POST'])
def capture_image():
    try:
        data = request.get_json()
        rtsp_url = data.get("rtsp_url")
        output_path = data.get("output_path", "./captures")
        os.makedirs(output_path, exist_ok=True)

        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            return jsonify({"error": "Failed to open RTSP stream"}), 500

        ret, frame = cap.read()
        cap.release()
        if not ret:
            return jsonify({"error": "Failed to capture frame"}), 500

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.jpg"
        filepath = os.path.join(output_path, filename)
        cv2.imwrite(filepath, frame)

        return jsonify({"status": "image captured", "file_path": filepath}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    port = int(os.environ.get('PORT', 7778))
    print(f"🚀 Starting Flask app on port {port}")
    print(f"🔧 API calls will be made to port {API_PORT}")
    app.run(host="0.0.0.0", port=port, debug=True)