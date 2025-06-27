# app.py

import os
from flask import Flask, request, jsonify
from libs.payload_sdk import PayloadSdkInterface, param_type
from libs.payload_define import *

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
    direction = request.json.get("zoomDirection")
    sdk.setCameraZoom(0.0, float(direction))
    return jsonify({"message": "스텝 줌이 설정되었습니다."})

@app.route("/camera/zoom/continuous", methods=["POST"])
def camera_zoom_continuous():
    direction = request.json.get("zoomDirection")
    sdk.setCameraZoom(1.0, float(direction))
    return jsonify({"message": "연속 줌이 설정되었습니다."})

@app.route("/camera/zoom/range", methods=["POST"])
def camera_zoom_range():
    zoom_percentage = request.json.get("zoomPercentage")
    sdk.setCameraZoom(2.0, float(zoom_percentage))
    return jsonify({"message": "레인지 줌이 설정되었습니다."})

@app.route("/camera/change-view-src", methods=["POST"])
def camera_change_view():
    view_src = request.json.get("viewSrc")
    sdk.setPayloadCameraParam("CAMERA_VIEW_SRC", int(view_src), param_type.PARAM_TYPE_UINT32)
    return jsonify({"message": "뷰 소스가 변경되었습니다."})

@app.route("/camera/focus/set-mode", methods=["POST"])
def camera_focus_mode():
    mode = request.json.get("focusMode")
    sdk.setPayloadCameraParam("CAMERA_FOCUS_MODE", int(mode), param_type.PARAM_TYPE_UINT32)
    return jsonify({"message": "포커스 모드가 설정되었습니다."})

@app.route("/camera/focus/continuous", methods=["POST"])
def camera_focus_continuous():
    direction = request.json.get("focusDirection")
    sdk.setCameraFocus(1.0, float(direction))
    return jsonify({"message": "포커스 값이 설정되었습니다."})

@app.route("/camera/focus/auto", methods=["POST"])
def camera_focus_auto():
    sdk.setCameraFocus(1.0)
    return jsonify({"message": "AUTO FOCUS"})

@app.route("/camera/set-ir-palette", methods=["POST"])
def camera_set_ir_palette():
    palette = request.json.get("irPalette")
    sdk.setPayloadCameraParam("CAMERA_IR_PALETTE", int(palette), param_type.PARAM_TYPE_UINT32)
    return jsonify({"message": "IR 팔레트가 설정되었습니다."})

@app.route("/camera/set-osd-mode", methods=["POST"])
def camera_set_osd_mode():
    osd_mode = request.json.get("osdMode")
    sdk.setPayloadCameraParam("CAMERA_OSD_MODE", int(osd_mode), param_type.PARAM_TYPE_UINT32)
    return jsonify({"message": "OSD 모드가 설정되었습니다."})

@app.route("/camera/set-flip-mode", methods=["POST"])
def camera_flip_mode():
    flip = request.json.get("flipMode")
    sdk.setPayloadCameraParam("CAMERA_FLIP_MODE", int(flip), param_type.PARAM_TYPE_UINT32)
    return jsonify({"message": "플립 모드가 설정되었습니다."})

@app.route("/camera/capture-image", methods=["POST"])
def camera_capture_image():
    sdk.setPayloadCameraCaptureImage(0)
    return jsonify({"message": "이미지 캡처가 실행되었습니다."})

@app.route("/camera/stop-capture", methods=["POST"])
def camera_stop_capture():
    sdk.setPayloadCameraStopImage()
    return jsonify({"message": "이미지 캡처가 중지되었습니다."})

@app.route("/camera/start-record", methods=["POST"])
def camera_start_record():
    sdk.setPayloadCameraRecordVideoStart()
    return jsonify({"message": "비디오 녹화가 시작되었습니다."})

@app.route("/camera/stop-record", methods=["POST"])
def camera_stop_record():
    sdk.setPayloadCameraRecordVideoStop()
    return jsonify({"message": "비디오 녹화가 중지되었습니다."})

@app.route("/camera/set-ffc-mode", methods=["POST"])
def camera_set_ffc_mode():
    mode = request.json.get("ffcMode")
    sdk.setPayloadCameraFFCMode(int(mode))
    return jsonify({"message": "FFC 모드가 설정되었습니다."})

@app.route("/camera/trigger-ffc", methods=["POST"])
def camera_trigger_ffc():
    sdk.setPayloadCameraFFCTrigg()
    return jsonify({"message": "FFC가 트리거되었습니다."})


# ------------------------ GimbalController ------------------------

@app.route("/gimbal/set-mode", methods=["POST"])
def gimbal_set_mode():
    mode = request.json.get("gimbalSetMode")
    sdk.setPayloadGimbalParamByID("GIMBAL_MODE", float(mode))
    return jsonify({"message": "모드가 설정되었습니다."})

@app.route("/gimbal/positionMove", methods=["POST"])
def gimbal_position_move():
    yaw = request.json.get("yaw")
    pitch = request.json.get("pitch")
    roll = request.json.get("roll")
    # 올바른 순서: pitch, roll, yaw
    sdk.setGimbalSpeed(float(pitch), float(roll), float(yaw), 1)
    return jsonify({"message": "짐벌 이동이 시작되었습니다."})

@app.route("/gimbal/continuousMove", methods=["POST"])
def gimbal_continuous_move():
    yaw = request.json.get("yaw")
    pitch = request.json.get("pitch")
    roll = request.json.get("roll")
    if float(yaw) == 0.0 and float(pitch) == 0.0 and float(roll) == 0.0:
        message = "짐벌 이동이 중지되었습니다."
    else:
        message = "짐벌 이동이 시작되었습니다."
    # 올바른 순서: pitch, roll, yaw
    sdk.setGimbalSpeed(float(pitch), float(roll), float(yaw), 0)
    return jsonify({"message": message})

@app.route("/gimbal/calib-gyro", methods=["POST"])
def gimbal_calib_gyro():
    sdk.sendPayloadGimbalCalibGyro()
    return jsonify({"message": "자이로 캘리브레이션이 시작되었습니다."})

@app.route("/gimbal/calib-accel", methods=["POST"])
def gimbal_calib_accel():
    sdk.sendPayloadGimbalCalibAccel()
    return jsonify({"message": "가속도 캘리브레이션이 시작되었습니다."})

@app.route("/gimbal/calib-motor", methods=["POST"])
def gimbal_calib_motor():
    sdk.sendPayloadGimbalCalibMotor()
    return jsonify({"message": "모터 캘리브레이션이 시작되었습니다."})

@app.route("/gimbal/search-home", methods=["POST"])
def gimbal_search_home():
    sdk.sendPayloadGimbalSearchHome()
    return jsonify({"message": "홈 위치 탐색이 시작되었습니다."})

@app.route("/gimbal/auto-tune", methods=["POST"])
def gimbal_auto_tune():
    status = request.json.get("status")
    sdk.sendPayloadGimbalAutoTune(bool(status))
    return jsonify({"message": "오토 튠이 실행되었습니다."})


if __name__ == "__main__":
    # 환경변수에서 포트 읽기 (기본값: 8000)
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)