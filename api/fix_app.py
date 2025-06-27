from flask import Flask, request, jsonify
from libs.payload_sdk import PayloadSdkInterface, param_type, input_mode_t, payload_status_event_t
from libs.payload_define import (
    PAYLOAD_CAMERA_VIEW_SRC,
    PAYLOAD_CAMERA_IR_PALETTE,
    PAYLOAD_CAMERA_VIDEO_OSD_MODE,
    PAYLOAD_CAMERA_VIDEO_FLIP,
    PAYLOAD_CAMERA_RC_MODE,
    payload_camera_rc_mode
)

import os
import logging
import signal
import sys


# === Flask & SDK 초기화 ===
app = Flask(__name__)
sdk = PayloadSdkInterface()
sdk.sdkInitConnection()
sdk.checkPayloadConnection()

# === 종료/시그널 핸들러 등록 ===
def quit_handler(sig, frame):
    print("\nTERMINATING AT USER REQUEST")
    try: sdk.sdkQuit()
    except Exception as e: print(f"Error while quitting payload: {e}")
    sys.exit(0)
    
    
signal.signal(signal.SIGINT, quit_handler)
# signal.signal(signal.SIGTERM, quit_handler)  # 필요시 추가

# === 짐벌 상태 콜백 (원할 때만 주석 해제) ===
# def onPayloadStatusChanged(event: int, param: list):
#     if payload_status_event_t(event) == payload_status_event_t.PAYLOAD_GB_ATTITUDE:
#         logging.info(f"[GIMBAL ATTITUDE] Pitch: {param[0]:.2f} - Roll: {param[1]:.2f} - Yaw: {param[2]:.2f}")
# sdk.regPayloadStatusChanged(onPayloadStatusChanged)


# ------------------------ CameraController ------------------------
"""카메라 제어 API
각종 카메라 관련 REST 엔드포인트
모든 엔드포인트에서 파라미터를 받아서 SDK에 명령을 전달 동작 상태를 로그로 남기고, 결과 메시지를 반환

줌(Zoom)
step, continuous, range 방식
뷰 소스/IR 팔레트/OSD/Flip 모드
포커스
모드, 연속 조작, 오토포커스
이미지 캡처/비디오 레코딩
촬영 시작, 정지, 레코딩 시작, 정지
FFC(Non-uniformity Correction) 모드/트리거
"""

@app.route("/camera/zoom/step", methods=["POST"])
def camera_zoom_step():
    direction = request.json.get("zoomDirection")
    logging.info(f"Camera step zoom: {direction}")
    sdk.setCameraZoom(0.0, float(direction))
    return jsonify({"message": "스텝 줌이 설정되었습니다."})

@app.route("/camera/zoom/continuous", methods=["POST"])
def camera_zoom_continuous():
    direction = request.json.get("zoomDirection")
    logging.info(f"Camera continuous zoom: {direction}")
    sdk.setCameraZoom(1.0, float(direction))
    return jsonify({"message": "연속 줌이 설정되었습니다."})

@app.route("/camera/zoom/range", methods=["POST"])
def camera_zoom_range():
    zoom_percentage = request.json.get("zoomPercentage")
    logging.info(f"Camera range zoom: {zoom_percentage}")
    sdk.setCameraZoom(2.0, float(zoom_percentage))
    return jsonify({"message": "레인지 줌이 설정되었습니다."})

@app.route("/camera/change-view-src", methods=["POST"])
def camera_change_view():
    view_src = request.json.get("viewSrc")
    logging.info(f"Change camera view src: {view_src}")
    # PAYLOAD_CAMERA_VIEW_SRC를 반드시 넣어줘야함.
    sdk.setPayloadCameraParam(PAYLOAD_CAMERA_VIEW_SRC, int(view_src), param_type.PARAM_TYPE_UINT32)
    return jsonify({"message": "뷰 소스가 변경되었습니다."})

@app.route("/camera/set-ir-palette", methods=["POST"])
def camera_set_ir_palette():
    palette = request.json.get("irPalette")
    logging.info(f"Set IR palette: {palette}")
    sdk.setPayloadCameraParam(PAYLOAD_CAMERA_IR_PALETTE, int(palette), param_type.PARAM_TYPE_UINT32)
    return jsonify({"message": "IR 팔레트가 설정되었습니다."})

@app.route("/camera/set-osd-mode", methods=["POST"])
def camera_set_osd_mode():
    osd_mode = request.json.get("osdMode")
    logging.info(f"Set OSD mode: {osd_mode}")
    sdk.setPayloadCameraParam(PAYLOAD_CAMERA_VIDEO_OSD_MODE, int(osd_mode), param_type.PARAM_TYPE_UINT32)
    return jsonify({"message": "OSD 모드가 설정되었습니다."})

@app.route("/camera/set-flip-mode", methods=["POST"])
def camera_flip_mode():
    flip = request.json.get("flipMode")
    logging.info(f"Set flip mode: {flip}")
    sdk.setPayloadCameraParam(PAYLOAD_CAMERA_VIDEO_FLIP, int(flip), param_type.PARAM_TYPE_UINT32)
    return jsonify({"message": "플립 모드가 설정되었습니다."})

@app.route("/camera/focus/set-mode", methods=["POST"])
def camera_focus_mode():
    mode = request.json.get("focusMode")
    logging.info(f"Set focus mode: {mode}")
    sdk.setPayloadCameraParam("C_V_FM", int(mode), param_type.PARAM_TYPE_UINT32)
    return jsonify({"message": "포커스 모드가 설정되었습니다."})

@app.route("/camera/focus/continuous", methods=["POST"])
def camera_focus_continuous():
    direction = request.json.get("focusDirection")
    logging.info(f"Continuous focus: {direction}")
    sdk.setCameraFocus(1.0, float(direction))
    return jsonify({"message": "포커스 값이 설정되었습니다."})

@app.route("/camera/focus/auto", methods=["POST"])
def camera_focus_auto():
    logging.info("Auto focus requested")
    sdk.setCameraFocus(1.0)
    return jsonify({"message": "AUTO FOCUS"})

@app.route("/camera/capture-image", methods=["POST"])
def camera_capture_image():
    logging.info("Image capture requested")
    sdk.setPayloadCameraCaptureImage(0)
    return jsonify({"message": "이미지 캡처가 실행되었습니다."})

@app.route("/camera/stop-capture", methods=["POST"])
def camera_stop_capture():
    logging.info("Stop image capture requested")
    sdk.setPayloadCameraStopImage()
    return jsonify({"message": "이미지 캡처가 중지되었습니다."})

@app.route("/camera/start-record", methods=["POST"])
def camera_start_record():
    logging.info("Start record requested")
    sdk.setPayloadCameraRecordVideoStart()
    return jsonify({"message": "비디오 녹화가 시작되었습니다."})

@app.route("/camera/stop-record", methods=["POST"])
def camera_stop_record():
    logging.info("Stop record requested")
    sdk.setPayloadCameraRecordVideoStop()
    return jsonify({"message": "비디오 녹화가 중지되었습니다."})

@app.route("/camera/set-ffc-mode", methods=["POST"])
def camera_set_ffc_mode():
    mode = request.json.get("ffcMode")
    logging.info(f"Set FFC mode: {mode}")
    sdk.setPayloadCameraFFCMode(int(mode))
    return jsonify({"message": "FFC 모드가 설정되었습니다."})

@app.route("/camera/trigger-ffc", methods=["POST"])
def camera_trigger_ffc():
    logging.info("FFC trigger requested")
    sdk.setPayloadCameraFFCTrigg()
    return jsonify({"message": "FFC가 트리거되었습니다."})

# ------------------------ GimbalController ------------------------
"""짐벌 제어 API

매핑(순서):
continuousMove/positionMove 등에서 반드시 sdk.setGimbalSpeed(pitch, roll,yaw ...) 순으로 매핑

예전에는 실수로 (pitch, roll, yaw)로 썼으나, 실제 동작 실험 결과 API 파라미터와 하드웨어 축이 맞게 pitch, roll,yaw 맞춰야 정상 동작

주요 API
Mode 설정:
/gimbal/set-mode - 짐벌 동작 모드 전환

RC 모드:
/gimbal/set-rc-mode - 외부 제어/리모컨 제어 등 모드 변경

연속 이동(속도 기반):
/gimbal/continuousMove - pitch/roll/yaw 값으로 지속적으로 움직임

위치 이동(각도 기반, positionMove):
현재는 기본적으로 속도 명령으로만 되어 있으나, SDK에 각도 이동 함수(setGimbalAngle 등)가 있으면 그 함수로 바꾸는 게 더 명확

정지:
/gimbal/stop

캘리브레이션:
자이로, 가속도, 모터

홈 위치, 오토튠 등:
/gimbal/search-home, /gimbal/auto-tune
"""

@app.route("/gimbal/set-mode", methods=["POST"])
def gimbal_set_mode():
    mode = request.json.get("gimbalSetMode")
    logging.info(f"Set gimbal mode: {mode}")
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
    yaw = float(request.json.get("yaw", 0))
    pitch = float(request.json.get("pitch", 0))
    roll = float(request.json.get("roll", 0))
    logging.info(f"Gimbal continuous move - yaw:{yaw}, pitch:{pitch}, roll:{roll}")
    
    # 명확한 매핑: pitch, roll, yaw  순서로 SDK에 전달
    sdk.setGimbalSpeed(pitch, roll, yaw,  input_mode_t.INPUT_SPEED)
    if yaw == 0.0 and pitch == 0.0 and roll == 0.0:
        message = "짐벌 이동이 중지되었습니다."
    else:
        message = "짐벌 이동이 시작되었습니다."
    return jsonify({"message": message})

@app.route("/gimbal/stop", methods=["POST"])
def gimbal_stop():
    sdk.setGimbalSpeed(0, 0, 0, input_mode_t.INPUT_SPEED)
    return jsonify({"message": "Gimbal movement stopped"})

@app.route("/gimbal/set-rc-mode", methods=["POST"])
def gimbal_set_rc_mode():
    mode = request.json.get("rcMode")
    if mode not in [payload_camera_rc_mode.PAYLOAD_CAMERA_RC_MODE_STANDARD, payload_camera_rc_mode.PAYLOAD_CAMERA_RC_MODE_GREMSY]:
        return jsonify({"error": "Invalid RC mode"}), 400
    sdk.setPayloadCameraParam(PAYLOAD_CAMERA_RC_MODE, int(mode), param_type.PARAM_TYPE_UINT32)
    return jsonify({"message": f"Gimbal RC 모드({mode})가 설정되었습니다."})

@app.route("/gimbal/calib-gyro", methods=["POST"])
def gimbal_calib_gyro():
    logging.info("Gimbal gyro calibration requested")
    sdk.sendPayloadGimbalCalibGyro()
    return jsonify({"message": "자이로 캘리브레이션이 시작되었습니다."})

@app.route("/gimbal/calib-accel", methods=["POST"])
def gimbal_calib_accel():
    logging.info("Gimbal accel calibration requested")
    sdk.sendPayloadGimbalCalibAccel()
    return jsonify({"message": "가속도 캘리브레이션이 시작되었습니다."})

@app.route("/gimbal/calib-motor", methods=["POST"])
def gimbal_calib_motor():
    logging.info("Gimbal motor calibration requested")
    sdk.sendPayloadGimbalCalibMotor()
    return jsonify({"message": "모터 캘리브레이션이 시작되었습니다."})

@app.route("/gimbal/search-home", methods=["POST"])
def gimbal_search_home():
    logging.info("Gimbal home search requested")
    sdk.sendPayloadGimbalSearchHome()
    return jsonify({"message": "홈 위치 탐색이 시작되었습니다."})

@app.route("/gimbal/auto-tune", methods=["POST"])
def gimbal_auto_tune():
    status = request.json.get("status")
    logging.info(f"Gimbal auto tune: {status}")
    sdk.sendPayloadGimbalAutoTune(bool(status))
    return jsonify({"message": "오토 튠이 실행되었습니다."})

if __name__ == "__main__":
    # 환경변수에서 포트 읽기 (기본값: 8000)
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting Flask app on port {port}")
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    app.run(host="0.0.0.0", port=port, debug=True)
    
    



# 동작 방식 및 실사용 주의점
"""
REST API 설계 원칙에 충실

각 기능별로 URL/엔드포인트 분리

파라미터를 body에 JSON으로 받아 사용

매핑(축 방향) 실수 방지

짐벌은 반드시 yaw, pitch, roll 순서로 SDK에 전달!

실험 결과를 반영한 안전한 매핑 구조

명령 실행 직후 상태 로그로 출력

짐벌 자세 변화 콜백(onPayloadStatusChanged)에서 로그를 남김

API 호출시마다 logging으로 기록(운영/디버깅 편리)

모드/제어권 전환 필수

/gimbal/set-rc-mode로 외부제어(RC/SDK) 권한 확보 후 명령을 보내야 모든 동작이 신뢰성 있게 동작

속도 vs 각도 구분

continuousMove: 속도 제어, 명령을 멈추면 바로 정지

positionMove: 각도 제어(아직 속도 방식만 구현, 추후 각도 기반 함수로 확장 추천)

호환성

각 카메라/짐벌 파라미터, 모드는 payload_define.py에서 상수로 정의, 가독성 및 실수 방지

"본 app.py는 REST API 기반의 카메라 및 짐벌 통합 제어 서버입니다.
카메라의 줌, IR 팔레트, OSD, 포커스, 캡처, 레코딩 등 모든 기능을 HTTP API로 일관성 있게 제공하며,
짐벌의 연속 이동, 위치 이동, 각종 캘리브레이션, 제어권 모드 변경 등 다양한 하드웨어 제어 명령도 하나의 API에서 바로 사용할 수 있습니다.
축 매핑 실수를 방지하기 위해 yaw, pitch, roll 순으로 SDK에 명령을 전달하며,
모든 요청과 하드웨어 피드백을 로그로 남겨 운영과 디버깅에 최적화했습니다."
"""