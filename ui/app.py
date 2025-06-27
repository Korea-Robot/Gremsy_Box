from flask import Flask, render_template, request, jsonify
import os
import logging
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 환경변수에서 API 포트 가져오기 (기본값: 6783)
API_PORT = int(os.environ.get('API_PORT', 6783))

# api는 전부 로컬에서 동작해야함.!!!

@app.route('/')
def index():
    # 클라이언트의 요청 호스트에서 IP만 추출해서 동적 webrtc 할당
    client_host = request.host.split(':')[0]
    mediamtx_url = f"http://{client_host}:8889/eo-ir-vio/"
    
    # 콘솔 디버깅용 로그 출력
    print(f"🔍 client_host: {client_host}")
    print(f"🔗 mediamtx_url: {mediamtx_url}")
    print(f"🔧 API_PORT: {API_PORT}")
    
    return render_template(
        'index.html',
        webrtc_url=mediamtx_url,
        robot_ip=client_host,
        api_port=API_PORT
    )

@app.route('/api/camera/<path:endpoint>', methods=['POST'])
def camera_proxy(endpoint):
    try:
        client_host = request.host.split(':')[0]
        api_url = f"http://127.0.0.1:{API_PORT}/camera/{endpoint}"
        
        response = requests.post(
            api_url,
            json=request.json,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        return jsonify({
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/gimbal/<path:endpoint>', methods=['POST'])
def gimbal_proxy(endpoint):
    try:
        client_host = request.host.split(':')[0]
        api_url = f"http://127.0.0.1:{API_PORT}/gimbal/{endpoint}"
        
        response = requests.post(
            api_url,
            json=request.json,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        return jsonify({
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 7777))
    print(f"🚀 Starting Flask app on port {port}")
    print(f"🔧 API calls will be made to port {API_PORT}")
    app.run(host="0.0.0.0", port=port, debug=True)