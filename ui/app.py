from flask import Flask, render_template, request, jsonify
import requests
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 설정
GREMSY_API_BASE = "http://100.88.88.66:8000"
ROBOT_IP = "192.168.168.105"
MEDIAMTX_HTTP_URL = f"http://{ROBOT_IP}:8889/gremsy/"

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html', 
                         rtsp_url=MEDIAMTX_HTTP_URL,
                         robot_ip=ROBOT_IP)

# 카메라 제어 API
@app.route('/api/camera/zoom/step', methods=['POST'])
def camera_zoom_step():
    try:
        data = request.get_json()
        zoom_direction = data.get('zoomDirection', 1)
        
        response = requests.post(
            f"{GREMSY_API_BASE}/camera/zoom/step",
            json={"zoomDirection": zoom_direction},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "스텝 줌이 설정되었습니다."})
        else:
            return jsonify({"status": "error", "message": "줌 설정 실패"}), 500
            
    except Exception as e:
        logging.error(f"Camera zoom step error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/camera/zoom/continuous', methods=['POST'])
def camera_zoom_continuous():
    try:
        data = request.get_json()
        zoom_direction = data.get('zoomDirection', 1)
        
        response = requests.post(
            f"{GREMSY_API_BASE}/camera/zoom/continuous",
            json={"zoomDirection": zoom_direction},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "연속 줌이 설정되었습니다."})
        else:
            return jsonify({"status": "error", "message": "줌 설정 실패"}), 500
            
    except Exception as e:
        logging.error(f"Camera zoom continuous error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/camera/zoom/range', methods=['POST'])
def camera_zoom_range():
    try:
        data = request.get_json()
        zoom_percentage = data.get('zoomPercentage', 50)
        
        response = requests.post(
            f"{GREMSY_API_BASE}/camera/zoom/range",
            json={"zoomPercentage": zoom_percentage},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "레인지 줌이 설정되었습니다."})
        else:
            return jsonify({"status": "error", "message": "줌 설정 실패"}), 500
            
    except Exception as e:
        logging.error(f"Camera zoom range error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/camera/view-source', methods=['POST'])
def camera_view_source():
    try:
        data = request.get_json()
        view_src = data.get('viewSrc', 0)
        
        response = requests.post(
            f"{GREMSY_API_BASE}/camera/change-view-src",
            json={"viewSrc": view_src},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "뷰 소스가 변경되었습니다."})
        else:
            return jsonify({"status": "error", "message": "뷰 소스 변경 실패"}), 500
            
    except Exception as e:
        logging.error(f"Camera view source error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/camera/ir-palette', methods=['POST'])
def camera_ir_palette():
    try:
        data = request.get_json()
        ir_palette = data.get('irPalette', 1)
        
        response = requests.post(
            f"{GREMSY_API_BASE}/camera/set-ir-palette",
            json={"irPalette": ir_palette},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "IR 팔레트가 설정되었습니다."})
        else:
            return jsonify({"status": "error", "message": "IR 팔레트 설정 실패"}), 500
            
    except Exception as e:
        logging.error(f"Camera IR palette error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/camera/osd-mode', methods=['POST'])
def camera_osd_mode():
    try:
        data = request.get_json()
        osd_mode = data.get('osdMode', 0)
        
        response = requests.post(
            f"{GREMSY_API_BASE}/camera/set-osd-mode",
            json={"osdMode": osd_mode},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "OSD 모드가 설정되었습니다."})
        else:
            return jsonify({"status": "error", "message": "OSD 모드 설정 실패"}), 500
            
    except Exception as e:
        logging.error(f"Camera OSD mode error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 짐벌 제어 API
@app.route('/api/gimbal/continuous-move', methods=['POST'])
def gimbal_continuous_move():
    try:
        data = request.get_json()
        yaw = float(data.get('yaw', 0))
        pitch = float(data.get('pitch', 0))
        roll = float(data.get('roll', 0))
        
        logging.info(f"Gimbal continuous move - yaw: {yaw}, pitch: {pitch}, roll: {roll}")
        
        response = requests.post(
            f"{GREMSY_API_BASE}/gimbal/continuousMove",
            json={"yaw": yaw, "pitch": pitch, "roll": roll},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            if yaw == 0 and pitch == 0 and roll == 0:
                return jsonify({"status": "success", "message": "짐벌 이동이 중지되었습니다."})
            else:
                return jsonify({"status": "success", "message": "짐벌 이동이 시작되었습니다."})
        else:
            logging.error(f"Gimbal API response error: {response.status_code} - {response.text}")
            return jsonify({"status": "error", "message": "짐벌 제어 실패"}), 500
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Gimbal continuous move request error: {e}")
        return jsonify({"status": "error", "message": f"API 요청 실패: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"Gimbal continuous move error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/gimbal/position-move', methods=['POST'])
def gimbal_position_move():
    try:
        data = request.get_json()
        yaw = float(data.get('yaw', 0))
        pitch = float(data.get('pitch', 0))
        roll = float(data.get('roll', 0))
        
        logging.info(f"Gimbal position move - yaw: {yaw}, pitch: {pitch}, roll: {roll}")
        
        response = requests.post(
            f"{GREMSY_API_BASE}/gimbal/positionMove",
            json={"yaw": yaw, "pitch": pitch, "roll": roll},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "짐벌 포지션 이동이 시작되었습니다."})
        else:
            logging.error(f"Gimbal position API response error: {response.status_code} - {response.text}")
            return jsonify({"status": "error", "message": "짐벌 포지션 이동 실패"}), 500
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Gimbal position move request error: {e}")
        return jsonify({"status": "error", "message": f"API 요청 실패: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"Gimbal position move error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/gimbal/reset', methods=['POST'])
def gimbal_reset():
    try:
        # 먼저 짐벌을 중지
        requests.post(
            f"{GREMSY_API_BASE}/gimbal/continuousMove",
            json={"yaw": 0, "pitch": 0, "roll": 0},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        # 그 다음 포지션을 0으로 초기화
        response = requests.post(
            f"{GREMSY_API_BASE}/gimbal/positionMove",
            json={"yaw": 0, "pitch": 0, "roll": 0},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "짐벌이 초기 위치로 리셋되었습니다."})
        else:
            return jsonify({"status": "error", "message": "짐벌 리셋 실패"}), 500
            
    except Exception as e:
        logging.error(f"Gimbal reset error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/gimbal/stop', methods=['POST'])
def gimbal_stop():
    try:
        response = requests.post(
            f"{GREMSY_API_BASE}/gimbal/continuousMove",
            json={"yaw": 0, "pitch": 0, "roll": 0},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "짐벌 이동이 중지되었습니다."})
        else:
            return jsonify({"status": "error", "message": "짐벌 중지 실패"}), 500
            
    except Exception as e:
        logging.error(f"Gimbal stop error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)