# 카메라 api.py

from flask import Flask, request, jsonify
from libs.payload_sdk import PayloadSdkInterface, param_type
from libs.payload_define import *
import os

# 플라스크 서버생성 
# 카메라 api.py

from flask import Flask, request, jsonify
from libs.payload_sdk import PayloadSdkInterface, param_type
from libs.payload_define import *
import os

# 플라스크 서버생성 
app = Flask(__name__)

# PayloadSdkInterface 초기화
sdk = PayloadSdkInterface()

# 연결 테스트
sdk.sdkInitConnection()
sdk.checkPayloadConnection()

# ------------------------ CameraController ------------------------

@app.route("/camera/zoom/step", methods=["POST"])
def camera_zoom_step():
    """스텝 줌 설정 - zoomDirection: 1 = 인, -1 = 아웃"""
    try:
        data = request.json
        if not data or "zoomDirection" not in data:
            return jsonify({"error": "zoomDirection 파라미터가 필요합니다."}), 400
        
        direction = int(data.get("zoomDirection"))
        if direction not in [-1, 1]:
            return jsonify({"error": "zoomDirection는 1(인) 또는 -1(아웃)이어야 합니다."}), 400
            
        sdk.setCameraZoom(0.0, float(direction))
        return jsonify({"message": "스텝 줌이 설정되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/camera/zoom/continuous", methods=["POST"])
def camera_zoom_continuous():
    """연속 줌 설정 - zoomDirection: 1 = 인, -1 = 아웃"""
    try:
        data = request.json
        if not data or "zoomDirection" not in data:
            return jsonify({"error": "zoomDirection 파라미터가 필요합니다."}), 400
        
        direction = int(data.get("zoomDirection"))
        if direction not in [-1, 1]:
            return jsonify({"error": "zoomDirection는 1(인) 또는 -1(아웃)이어야 합니다."}), 400
            
        sdk.setCameraZoom(1.0, float(direction))
        return jsonify({"message": "연속 줌이 설정되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/camera/zoom/range", methods=["POST"])
def camera_zoom_range():
    """레인지 줌 설정 - zoomPercentage: 0~100"""
    try:
        data = request.json
        if not data or "zoomPercentage" not in data:
            return jsonify({"error": "zoomPercentage 파라미터가 필요합니다."}), 400
        
        zoom_percentage = int(data.get("zoomPercentage"))
        if not 0 <= zoom_percentage <= 100:
            return jsonify({"error": "zoomPercentage는 0~100 사이의 값이어야 합니다."}), 400
            
        sdk.setCameraZoom(2.0, float(zoom_percentage))
        return jsonify({"message": "레인지 줌이 설정되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/camera/change-view-src", methods=["POST"])
def camera_change_view():
    """카메라 뷰 소스 변경 - viewSrc: 0=EO/IR통합, 1=EO, 2=IR, 3=IR/EO전환, 4=동기화뷰"""
    try:
        data = request.json
        if not data or "viewSrc" not in data:
            return jsonify({"error": "viewSrc 파라미터가 필요합니다."}), 400
        
        view_src = int(data.get("viewSrc"))
        if not 0 <= view_src <= 4:
            return jsonify({"error": "viewSrc는 0~4 사이의 값이어야 합니다."}), 400
            
        sdk.setPayloadCameraParam("CAMERA_VIEW_SRC", view_src, param_type.PARAM_TYPE_UINT32)
        return jsonify({"message": "뷰 소스가 변경되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/camera/focus/set-mode", methods=["POST"])
def camera_focus_mode():
    """포커스 모드 설정 - focusMode: 0=수동, 1=줌트리거, 2=자동근거리, 3=자동원거리"""
    try:
        data = request.json
        if not data or "focusMode" not in data:
            return jsonify({"error": "focusMode 파라미터가 필요합니다."}), 400
        
        mode = int(data.get("focusMode"))
        if not 0 <= mode <= 3:
            return jsonify({"error": "focusMode는 0~3 사이의 값이어야 합니다."}), 400
            
        sdk.setPayloadCameraParam("CAMERA_FOCUS_MODE", mode, param_type.PARAM_TYPE_UINT32)
        return jsonify({"message": "포커스 모드가 설정되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/camera/focus/continuous", methods=["POST"])
def camera_focus_continuous():
    """연속 포커스 조정 - focusDirection: -1=안쪽, 1=무한대, 0=정지"""
    try:
        data = request.json
        if not data or "focusDirection" not in data:
            return jsonify({"error": "focusDirection 파라미터가 필요합니다."}), 400
        
        direction = int(data.get("focusDirection"))
        if direction not in [-1, 0, 1]:
            return jsonify({"error": "focusDirection는 -1(안쪽), 0(정지), 1(무한대) 중 하나여야 합니다."}), 400
            
        sdk.setCameraFocus(1.0, float(direction))
        return jsonify({"message": "포커스 값이 설정되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/camera/focus/auto", methods=["POST"])
def camera_focus_auto():
    """자동 포커스 설정"""
    try:
        sdk.setCameraFocus(1.0)
        return jsonify({"message": "AUTO FOCUS"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/camera/set-ir-palette", methods=["POST"])
def camera_set_ir_palette():
    """IR 팔레트 설정 - irPalette: 1~10 (화이트핫, 블랙핫, 레인보우 등)"""
    try:
        data = request.json
        if not data or "irPalette" not in data:
            return jsonify({"error": "irPalette 파라미터가 필요합니다."}), 400
        
        palette = int(data.get("irPalette"))
        if not 1 <= palette <= 10:
            return jsonify({"error": "irPalette는 1~10 사이의 값이어야 합니다."}), 400
            
        sdk.setPayloadCameraParam("CAMERA_IR_PALETTE", palette, param_type.PARAM_TYPE_UINT32)
        return jsonify({"message": "IR 팔레트가 설정되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/camera/set-osd-mode", methods=["POST"])
def camera_set_osd_mode():
    """OSD 모드 설정 - osdMode: 0=비활성화, 1=디버그모드, 2=상태정보표시"""
    try:
        data = request.json
        if not data or "osdMode" not in data:
            return jsonify({"error": "osdMode 파라미터가 필요합니다."}), 400
        
        osd_mode = int(data.get("osdMode"))
        if not 0 <= osd_mode <= 2:
            return jsonify({"error": "osdMode는 0~2 사이의 값이어야 합니다."}), 400
            
        sdk.setPayloadCameraParam("CAMERA_OSD_MODE", osd_mode, param_type.PARAM_TYPE_UINT32)
        return jsonify({"message": "OSD 모드가 설정되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/camera/set-flip-mode", methods=["POST"])
def camera_set_flip_mode():
    """플립 모드 설정 - flipMode: 2=플립켬, 3=플립끔"""
    try:
        data = request.json
        if not data or "flipMode" not in data:
            return jsonify({"error": "flipMode 파라미터가 필요합니다."}), 400
        
        flip = int(data.get("flipMode"))
        if flip not in [2, 3]:
            return jsonify({"error": "flipMode는 2(플립켬) 또는 3(플립끔)이어야 합니다."}), 400
            
        sdk.setPayloadCameraParam("CAMERA_FLIP_MODE", flip, param_type.PARAM_TYPE_UINT32)
        return jsonify({"message": "플립 모드가 설정되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/camera/capture-image", methods=["POST"])
def camera_capture_image():
    """이미지 캡처"""
    try:
        sdk.setPayloadCameraCaptureImage(0)
        return jsonify({"message": "이미지 캡처가 실행되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/camera/stop-capture", methods=["POST"])
def camera_stop_capture():
    """이미지 캡처 중지"""
    try:
        sdk.setPayloadCameraStopImage()
        return jsonify({"message": "이미지 캡처가 중지되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/camera/start-record", methods=["POST"])
def camera_start_record():
    """비디오 녹화 시작"""
    try:
        sdk.setPayloadCameraRecordVideoStart()
        return jsonify({"message": "비디오 녹화가 시작되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/camera/stop-record", methods=["POST"])
def camera_stop_record():
    """비디오 녹화 중지"""
    try:
        sdk.setPayloadCameraRecordVideoStop()
        return jsonify({"message": "비디오 녹화가 중지되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/camera/set-ffc-mode", methods=["POST"])
def camera_set_ffc_mode():
    """FFC 모드 설정"""
    try:
        data = request.json
        if not data or "ffcMode" not in data:
            return jsonify({"error": "ffcMode 파라미터가 필요합니다."}), 400
        
        mode = int(data.get("ffcMode"))
        sdk.setPayloadCameraFFCMode(mode)
        return jsonify({"message": "FFC 모드가 설정되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/camera/trigger-ffc", methods=["POST"])
def camera_trigger_ffc():
    """FFC 트리거"""
    try:
        sdk.setPayloadCameraFFCTrigg()
        return jsonify({"message": "FFC가 트리거되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------ GimbalController ------------------------

@app.route("/gimbal/set-mode", methods=["POST"])
def gimbal_set_mode():
    """짐벌 모드 설정"""
    try:
        data = request.json
        if not data or "gimbalSetMode" not in data:
            return jsonify({"error": "gimbalSetMode 파라미터가 필요합니다."}), 400
        
        mode = float(data.get("gimbalSetMode"))
        sdk.setPayloadGimbalParamByID("GIMBAL_MODE", mode)
        return jsonify({"message": "모드가 설정되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/gimbal/positionMove", methods=["POST"])
def gimbal_position_move():
    """짐벌 위치 이동"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "yaw, pitch, roll 파라미터가 필요합니다."}), 400
        
        yaw = float(data.get("yaw", 0))
        pitch = float(data.get("pitch", 0))
        roll = float(data.get("roll", 0))
        
        # 올바른 순서: pitch, roll, yaw
        sdk.setGimbalSpeed(pitch, roll, yaw, 1)
        return jsonify({"message": "짐벌 이동이 시작되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/gimbal/continuousMove", methods=["POST"])
def gimbal_continuous_move():
    """짐벌 연속 이동"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "yaw, pitch, roll 파라미터가 필요합니다."}), 400
        
        yaw = float(data.get("yaw", 0))
        pitch = float(data.get("pitch", 0))
        roll = float(data.get("roll", 0))
        
        if yaw == 0.0 and pitch == 0.0 and roll == 0.0:
            message = "짐벌 이동이 중지되었습니다."
        else:
            message = "짐벌 이동이 시작되었습니다."
        
        # 올바른 순서: pitch, roll, yaw
        sdk.setGimbalSpeed(pitch, roll, yaw, 0)
        return jsonify({"message": message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/gimbal/calib-gyro", methods=["POST"])
def gimbal_calib_gyro():
    """자이로 캘리브레이션"""
    try:
        sdk.sendPayloadGimbalCalibGyro()
        return jsonify({"message": "자이로 캘리브레이션이 시작되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/gimbal/calib-accel", methods=["POST"])
def gimbal_calib_accel():
    """가속도 캘리브레이션"""
    try:
        sdk.sendPayloadGimbalCalibAccel()
        return jsonify({"message": "가속도 캘리브레이션이 시작되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/gimbal/calib-motor", methods=["POST"])
def gimbal_calib_motor():
    """모터 캘리브레이션"""
    try:
        sdk.sendPayloadGimbalCalibMotor()
        return jsonify({"message": "모터 캘리브레이션이 시작되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/gimbal/search-home", methods=["POST"])
def gimbal_search_home():
    """홈 위치 탐색"""
    try:
        sdk.sendPayloadGimbalSearchHome()
        return jsonify({"message": "홈 위치 탐색이 시작되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/gimbal/auto-tune", methods=["POST"])
def gimbal_auto_tune():
    """오토 튠"""
    try:
        data = request.json
        if not data or "status" not in data:
            return jsonify({"error": "status 파라미터가 필요합니다."}), 400
        
        status = bool(data.get("status"))
        sdk.sendPayloadGimbalAutoTune(status)
        return jsonify({"message": "오토 튠이 실행되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------ 헬스 체크 및 상태 확인 ------------------------

@app.route("/health", methods=["GET"])
def health_check():
    """서버 상태 확인"""
    return jsonify({"status": "healthy", "message": "카메라 API 서버가 정상 동작 중입니다."})

@app.route("/camera/status", methods=["GET"])
def camera_status():
    """카메라 연결 상태 확인"""
    try:
        # 연결 상태 확인 (실제 구현에 따라 다를 수 있음)
        sdk.checkPayloadConnection()
        return jsonify({"status": "connected", "message": "카메라가 정상적으로 연결되었습니다."})
    except Exception as e:
        return jsonify({"status": "disconnected", "error": str(e)}), 500

# ------------------------ 에러 핸들러 ------------------------

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "요청하신 엔드포인트를 찾을 수 없습니다."}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "허용되지 않은 HTTP 메소드입니다."}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "내부 서버 오류가 발생했습니다."}), 500


# if __name__ == "__main__":
#     # 환경변수에서 포트 읽기 (기본값: 8000)
#     port = int(os.environ.get('PORT', 8000))
#     print(f"Starting Flask app on port {port}")
#     print("Available endpoints:")
#     print("  Camera Controls:")
#     print("    POST /camera/zoom/step")
#     print("    POST /camera/zoom/continuous") 
#     print("    POST /camera/zoom/range")
#     print("    POST /camera/change-view-src")
#     print("    POST /camera/focus/set-mode")
#     print("    POST /camera/focus/continuous")
#     print("    POST /camera/focus/auto")
#     print("    POST /camera/set-ir-palette")
#     print("    POST /camera/set-osd-mode")
#     print("    POST /camera/set-flip-mode")
#     print("    POST /camera/capture-image")
#     print("    POST /camera/stop-capture")
#     print("    POST /camera/start-record")
#     print("    POST /camera/stop-record")
#     print("    POST /camera/set-ffc-mode")
#     print("    POST /camera/trigger-ffc")
#     print("  Gimbal Controls:")
#     print("    POST /gimbal/set-mode")
#     print("    POST /gimbal/positionMove")
#     print("    POST /gimbal/continuousMove")
#     print("    POST /gimbal/calib-gyro")
#     print("    POST /gimbal/calib-accel")
#     print("    POST /gimbal/calib-motor")
#     print("    POST /gimbal/search-home")
#     print("    POST /gimbal/auto-tune")
#     print("  Status:")
#     print("    GET  /health")
#     print("    GET  /camera/status")
#     print()
#     app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    # 환경변수에서 포트 읽기 (기본값: 8000)
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)