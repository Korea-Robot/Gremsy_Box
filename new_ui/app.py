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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 7777))
    print(f"🚀 Starting Flask app on port {port}")
    print(f"🔧 API calls will be made to port {API_PORT}")
    app.run(host="0.0.0.0", port=port, debug=True)