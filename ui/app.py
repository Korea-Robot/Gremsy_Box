from flask import Flask, render_template, request, jsonify
import requests
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 설정
GREMSY_API_BASE = "http://localhost:8000"
ROBOT_IP = "192.168.168.105"
MEDIAMTX_RTSP_URL = f"rtsp://{ROBOT_IP}:8554/gremsy"
MEDIAMTX_HTTP_URL = f"http://{ROBOT_IP}:8889/gremsy/"

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html', 
                         rtsp_url=MEDIAMTX_RTSP_URL,
                         robot_ip=ROBOT_IP)

@app.route('/api/gimbal/move', methods=['POST'])
def gimbal_move():
    """짐벌 연속 이동"""
    try:
        data = request.get_json()
        yaw = data.get('yaw', 0)
        pitch = data.get('pitch', 0)
        roll = data.get('roll', 0)
        
        response = requests.post(
            f"{GREMSY_API_BASE}/gimbal/continuousMove",
            headers={'Content-Type': 'application/json'},
            json={'yaw': yaw, 'pitch': pitch, 'roll': roll},
            timeout=5
        )
        
        return jsonify({
            'success': True,
            'status_code': response.status_code,
            'response': response.text
        })
    except Exception as e:
        logging.error(f"Gimbal move error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/gimbal/stop', methods=['POST'])
def gimbal_stop():
    """짐벌 정지"""
    try:
        response = requests.post(f"{GREMSY_API_BASE}/gimbal/stop", timeout=5)
        return jsonify({
            'success': True,
            'status_code': response.status_code,
            'response': response.text
        })
    except Exception as e:
        logging.error(f"Gimbal stop error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/camera/ir-palette', methods=['POST'])
def set_ir_palette():
    """IR 팔레트 변경"""
    try:
        data = request.get_json()
        ir_palette = data.get('irPalette', 1)
        
        response = requests.post(
            f"{GREMSY_API_BASE}/camera/set-ir-palette",
            headers={'Content-Type': 'application/json'},
            json={'irPalette': ir_palette},
            timeout=5
        )
        
        return jsonify({
            'success': True,
            'status_code': response.status_code,
            'response': response.text
        })
    except Exception as e:
        logging.error(f"IR palette error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/camera/view-src', methods=['POST'])
def change_view_src():
    """뷰소스 변경"""
    try:
        data = request.get_json()
        view_src = data.get('viewSrc', 1)
        
        response = requests.post(
            f"{GREMSY_API_BASE}/camera/change-view-src",
            headers={'Content-Type': 'application/json'},
            json={'viewSrc': view_src},
            timeout=5
        )
        
        return jsonify({
            'success': True,
            'status_code': response.status_code,
            'response': response.text
        })
    except Exception as e:
        logging.error(f"View source error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stream/status', methods=['GET'])
def stream_status():
    """MediaMTX 스트림 상태 확인"""
    try:
        response = requests.get(f"{MEDIAMTX_HTTP_URL}/api/paths", timeout=5)
        return jsonify({
            'success': True,
            'paths': response.json()
        })
    except Exception as e:
        logging.error(f"Stream status error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)