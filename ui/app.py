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

# ======================== 기존 API 엔드포인트 ========================

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
        response = requests.post(
            f"{GREMSY_API_BASE}/gimbal/continuousMove",
            headers={'Content-Type': 'application/json'},
            json={'yaw': 0, 'pitch': 0, 'roll': 0},
            timeout=5
        )
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
        response = requests.get(f"{MEDIAMTX_HTTP_URL}api/paths", timeout=5)
        return jsonify({
            'success': True,
            'paths': response.json()
        })
    except Exception as e:
        logging.error(f"Stream status error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ======================== 추가 API 엔드포인트 ========================

def proxy_to_gremsy(endpoint, data=None):
    """Gremsy API 프록시 함수"""
    try:
        url = f"{GREMSY_API_BASE}{endpoint}"
        if data:
            response = requests.post(url, 
                                   headers={'Content-Type': 'application/json'},
                                   json=data, timeout=5)
        else:
            response = requests.post(url, timeout=5)
        
        return jsonify({
            'success': True,
            'status_code': response.status_code,
            'response': response.text
        })
    except Exception as e:
        logging.error(f"Proxy error for {endpoint}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 짐벌 관련 API
@app.route('/api/gimbal/set-mode', methods=['POST'])
def gimbal_set_mode():
    data = request.get_json()
    return proxy_to_gremsy('/gimbal/set-mode', {'gimbalSetMode': data.get('gimbalSetMode')})

@app.route('/api/gimbal/position-move', methods=['POST'])
def gimbal_position_move():
    data = request.get_json()
    return proxy_to_gremsy('/gimbal/positionMove', data)

@app.route('/api/gimbal/calib-gyro', methods=['POST'])
def gimbal_calib_gyro():
    return proxy_to_gremsy('/gimbal/calib-gyro')

@app.route('/api/gimbal/calib-accel', methods=['POST'])
def gimbal_calib_accel():
    return proxy_to_gremsy('/gimbal/calib-accel')

@app.route('/api/gimbal/calib-motor', methods=['POST'])
def gimbal_calib_motor():
    return proxy_to_gremsy('/gimbal/calib-motor')

@app.route('/api/gimbal/search-home', methods=['POST'])
def gimbal_search_home():
    return proxy_to_gremsy('/gimbal/search-home')

@app.route('/api/gimbal/auto-tune', methods=['POST'])
def gimbal_auto_tune():
    data = request.get_json()
    return proxy_to_gremsy('/gimbal/auto-tune', {'status': data.get('status')})

# 카메라 줌 관련 API
@app.route('/api/camera/zoom/step', methods=['POST'])
def camera_zoom_step():
    data = request.get_json()
    return proxy_to_gremsy('/camera/zoom/step', {'zoomDirection': data.get('zoomDirection')})

@app.route('/api/camera/zoom/continuous', methods=['POST'])
def camera_zoom_continuous():
    data = request.get_json()
    return proxy_to_gremsy('/camera/zoom/continuous', {'zoomDirection': data.get('zoomDirection')})

@app.route('/api/camera/zoom/range', methods=['POST'])
def camera_zoom_range():
    data = request.get_json()
    return proxy_to_gremsy('/camera/zoom/range', {'zoomPercentage': data.get('zoomPercentage')})

# 카메라 포커스 관련 API
@app.route('/api/camera/focus/set-mode', methods=['POST'])
def camera_focus_set_mode():
    data = request.get_json()
    return proxy_to_gremsy('/camera/focus/set-mode', {'focusMode': data.get('focusMode')})

@app.route('/api/camera/focus/continuous', methods=['POST'])
def camera_focus_continuous():
    data = request.get_json()
    return proxy_to_gremsy('/camera/focus/continuous', {'focusDirection': data.get('focusDirection')})

@app.route('/api/camera/focus/auto', methods=['POST'])
def camera_focus_auto():
    return proxy_to_gremsy('/camera/focus/auto')

# 카메라 설정 관련 API
@app.route('/api/camera/set-osd-mode', methods=['POST'])
def camera_set_osd_mode():
    data = request.get_json()
    return proxy_to_gremsy('/camera/set-osd-mode', {'osdMode': data.get('osdMode')})

@app.route('/api/camera/set-flip-mode', methods=['POST'])
def camera_set_flip_mode():
    data = request.get_json()
    return proxy_to_gremsy('/camera/set-flip-mode', {'flipMode': data.get('flipMode')})

# 카메라 캡처/녹화 관련 API
@app.route('/api/camera/capture-image', methods=['POST'])
def camera_capture_image():
    return proxy_to_gremsy('/camera/capture-image')

@app.route('/api/camera/stop-capture', methods=['POST'])
def camera_stop_capture():
    return proxy_to_gremsy('/camera/stop-capture')

@app.route('/api/camera/start-record', methods=['POST'])
def camera_start_record():
    return proxy_to_gremsy('/camera/start-record')

@app.route('/api/camera/stop-record', methods=['POST'])
def camera_stop_record():
    return proxy_to_gremsy('/camera/stop-record')

# FFC 관련 API
@app.route('/api/camera/set-ffc-mode', methods=['POST'])
def camera_set_ffc_mode():
    data = request.get_json()
    return proxy_to_gremsy('/camera/set-ffc-mode', {'ffcMode': data.get('ffcMode')})

@app.route('/api/camera/trigger-ffc', methods=['POST'])
def camera_trigger_ffc():
    return proxy_to_gremsy('/camera/trigger-ffc')

# 상태 확인 API
@app.route('/api/status', methods=['GET'])
def get_status():
    """전체 시스템 상태 확인"""
    try:
        # Gremsy API 연결 테스트
        gremsy_status = False
        try:
            response = requests.get(f"{GREMSY_API_BASE}/status", timeout=2)
            gremsy_status = response.status_code == 200
        except:
            pass
        
        # MediaMTX 상태 확인
        stream_status = False
        try:
            response = requests.get(f"{MEDIAMTX_HTTP_URL}api/paths", timeout=2)
            stream_status = response.status_code == 200
        except:
            pass
        
        return jsonify({
            'success': True,
            'gremsy_connected': gremsy_status,
            'stream_available': stream_status,
            'timestamp': json.dumps(datetime.now(), default=str)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777, debug=True)