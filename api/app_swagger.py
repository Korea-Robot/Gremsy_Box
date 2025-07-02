from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields, Namespace
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

# === Flask & API 초기화 ===
app = Flask(__name__)
api = Api(
    app, 
    version='1.0', 
    title='Payload Control API',
    description='카메라 및 짐벌 통합 제어를 위한 REST API',
    doc='/swagger/',
    prefix='/api'
)

# 네임스페이스 정의
camera_ns = Namespace('camera', description='카메라 제어 관련 API')
gimbal_ns = Namespace('gimbal', description='짐벌 제어 관련 API')

api.add_namespace(camera_ns)
api.add_namespace(gimbal_ns)

# === SDK 초기화 ===
sdk = PayloadSdkInterface()
sdk.sdkInitConnection()
sdk.checkPayloadConnection()

# === 종료/시그널 핸들러 등록 ===
def quit_handler(sig, frame):
    print("\nTERMINATING AT USER REQUEST")
    try: 
        sdk.sdkQuit()
    except Exception as e: 
        print(f"Error while quitting payload: {e}")
    sys.exit(0)

signal.signal(signal.SIGINT, quit_handler)

# === 모델 정의 ===
# 카메라 모델
zoom_step_model = api.model('ZoomStep', {
    'zoomDirection': fields.Float(required=True, description='줌 방향 (-1.0 ~ 1.0)', example=1.0)
})

zoom_continuous_model = api.model('ZoomContinuous', {
    'zoomDirection': fields.Float(required=True, description='연속 줌 방향 (-1.0 ~ 1.0)', example=0.5)
})

zoom_range_model = api.model('ZoomRange', {
    'zoomPercentage': fields.Float(required=True, description='줌 백분율 (0.0 ~ 100.0)', example=50.0)
})

view_src_model = api.model('ViewSource', {
    'viewSrc': fields.Integer(required=True, description='뷰 소스 (0: RGB, 1: IR)', example=0)
})

ir_palette_model = api.model('IRPalette', {
    'irPalette': fields.Integer(required=True, description='IR 팔레트 번호 (0~255)', example=1)
})

osd_mode_model = api.model('OSDMode', {
    'osdMode': fields.Integer(required=True, description='OSD 모드 (0: OFF, 1: ON)', example=1)
})

flip_mode_model = api.model('FlipMode', {
    'flipMode': fields.Integer(required=True, description='플립 모드 (0: Normal, 1: Horizontal, 2: Vertical, 3: Both)', example=0)
})

focus_mode_model = api.model('FocusMode', {
    'focusMode': fields.Integer(required=True, description='포커스 모드 (0: Manual, 1: Auto)', example=1)
})

focus_continuous_model = api.model('FocusContinuous', {
    'focusDirection': fields.Float(required=True, description='포커스 방향 (-1.0 ~ 1.0)', example=0.5)
})

ffc_mode_model = api.model('FFCMode', {
    'ffcMode': fields.Integer(required=True, description='FFC 모드 (0: Manual, 1: Auto)', example=1)
})

# 짐벌 모델
gimbal_mode_model = api.model('GimbalMode', {
    'gimbalSetMode': fields.Integer(required=True, description='짐벌 모드 (0: Lock, 1: Follow, 2: FPV)', example=1)
})

gimbal_position_model = api.model('GimbalPosition', {
    'yaw': fields.Float(required=True, description='Yaw 각도 (-180 ~ 180)', example=0.0),
    'pitch': fields.Float(required=True, description='Pitch 각도 (-90 ~ 90)', example=0.0),
    'roll': fields.Float(required=True, description='Roll 각도 (-180 ~ 180)', example=0.0)
})

gimbal_continuous_model = api.model('GimbalContinuous', {
    'yaw': fields.Float(required=False, description='Yaw 속도 (-100 ~ 100)', example=0.0, default=0.0),
    'pitch': fields.Float(required=False, description='Pitch 속도 (-100 ~ 100)', example=0.0, default=0.0),
    'roll': fields.Float(required=False, description='Roll 속도 (-100 ~ 100)', example=0.0, default=0.0)
})

rc_mode_model = api.model('RCMode', {
    'rcMode': fields.Integer(required=True, description='RC 모드 (0: Standard, 1: Gremsy)', example=0)
})

auto_tune_model = api.model('AutoTune', {
    'status': fields.Boolean(required=True, description='오토 튠 상태 (true: 시작, false: 중지)', example=True)
})

# 공통 응답 모델
success_response = api.model('SuccessResponse', {
    'message': fields.String(description='성공 메시지')
})

error_response = api.model('ErrorResponse', {
    'error': fields.String(description='에러 메시지')
})

# ======================== 카메라 API ========================
@camera_ns.route('/zoom/step')
class CameraZoomStep(Resource):
    @camera_ns.expect(zoom_step_model)
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_zoom_step', description='카메라 스텝 줌 제어')
    def post(self):
        """카메라 스텝 줌 제어
        
        한 단계씩 줌을 조절합니다.
        - zoomDirection: 양수는 줌인, 음수는 줌아웃
        """
        direction = request.json.get("zoomDirection")
        logging.info(f"Camera step zoom: {direction}")
        sdk.setCameraZoom(0.0, float(direction))
        return {"message": "스텝 줌이 설정되었습니다."}

@camera_ns.route('/zoom/continuous')
class CameraZoomContinuous(Resource):
    @camera_ns.expect(zoom_continuous_model)
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_zoom_continuous', description='카메라 연속 줌 제어')
    def post(self):
        """카메라 연속 줌 제어
        
        지속적으로 줌을 조절합니다.
        - zoomDirection: 연속 줌 속도 (-1.0 ~ 1.0)
        """
        direction = request.json.get("zoomDirection")
        logging.info(f"Camera continuous zoom: {direction}")
        sdk.setCameraZoom(1.0, float(direction))
        return {"message": "연속 줌이 설정되었습니다."}

@camera_ns.route('/zoom/range')
class CameraZoomRange(Resource):
    @camera_ns.expect(zoom_range_model)
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_zoom_range', description='카메라 레인지 줌 제어')
    def post(self):
        """카메라 레인지 줌 제어
        
        특정 줌 레벨로 직접 이동합니다.
        - zoomPercentage: 줌 백분율 (0.0 ~ 100.0)
        """
        zoom_percentage = request.json.get("zoomPercentage")
        logging.info(f"Camera range zoom: {zoom_percentage}")
        sdk.setCameraZoom(2.0, float(zoom_percentage))
        return {"message": "레인지 줌이 설정되었습니다."}

@camera_ns.route('/change-view-src')
class CameraChangeView(Resource):
    @camera_ns.expect(view_src_model)
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_change_view', description='카메라 뷰 소스 변경')
    def post(self):
        """카메라 뷰 소스 변경
        
        RGB 카메라와 적외선 카메라 간 전환합니다.
        - viewSrc: 0 (RGB), 1 (IR)
        """
        view_src = request.json.get("viewSrc")
        logging.info(f"Change camera view src: {view_src}")
        sdk.setPayloadCameraParam(PAYLOAD_CAMERA_VIEW_SRC, int(view_src), param_type.PARAM_TYPE_UINT32)
        return {"message": "뷰 소스가 변경되었습니다."}

@camera_ns.route('/set-ir-palette')
class CameraSetIRPalette(Resource):
    @camera_ns.expect(ir_palette_model)
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_set_ir_palette', description='적외선 팔레트 설정')
    def post(self):
        """적외선 팔레트 설정
        
        적외선 이미지의 색상 팔레트를 변경합니다.
        - irPalette: 팔레트 번호 (0~255)
        """
        palette = request.json.get("irPalette")
        logging.info(f"Set IR palette: {palette}")
        sdk.setPayloadCameraParam(PAYLOAD_CAMERA_IR_PALETTE, int(palette), param_type.PARAM_TYPE_UINT32)
        return {"message": "IR 팔레트가 설정되었습니다."}

@camera_ns.route('/set-osd-mode')
class CameraSetOSDMode(Resource):
    @camera_ns.expect(osd_mode_model)
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_set_osd_mode', description='OSD 모드 설정')
    def post(self):
        """OSD(On-Screen Display) 모드 설정
        
        화면 오버레이 정보 표시를 제어합니다.
        - osdMode: 0 (OFF), 1 (ON)
        """
        osd_mode = request.json.get("osdMode")
        logging.info(f"Set OSD mode: {osd_mode}")
        sdk.setPayloadCameraParam(PAYLOAD_CAMERA_VIDEO_OSD_MODE, int(osd_mode), param_type.PARAM_TYPE_UINT32)
        return {"message": "OSD 모드가 설정되었습니다."}

@camera_ns.route('/set-flip-mode')
class CameraFlipMode(Resource):
    @camera_ns.expect(flip_mode_model)
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_flip_mode', description='영상 플립 모드 설정')
    def post(self):
        """영상 플립 모드 설정
        
        영상의 방향을 제어합니다.
        - flipMode: 0 (Normal), 1 (Horizontal), 2 (Vertical), 3 (Both)
        """
        flip = request.json.get("flipMode")
        logging.info(f"Set flip mode: {flip}")
        sdk.setPayloadCameraParam(PAYLOAD_CAMERA_VIDEO_FLIP, int(flip), param_type.PARAM_TYPE_UINT32)
        return {"message": "플립 모드가 설정되었습니다."}

@camera_ns.route('/focus/set-mode')
class CameraFocusMode(Resource):
    @camera_ns.expect(focus_mode_model)
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_focus_mode', description='포커스 모드 설정')
    def post(self):
        """포커스 모드 설정
        
        포커스 제어 방식을 변경합니다.
        - focusMode: 0 (Manual), 1 (Auto)
        """
        mode = request.json.get("focusMode")
        logging.info(f"Set focus mode: {mode}")
        sdk.setPayloadCameraParam("C_V_FM", int(mode), param_type.PARAM_TYPE_UINT32)
        return {"message": "포커스 모드가 설정되었습니다."}

@camera_ns.route('/focus/continuous')
class CameraFocusContinuous(Resource):
    @camera_ns.expect(focus_continuous_model)
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_focus_continuous', description='연속 포커스 제어')
    def post(self):
        """연속 포커스 제어
        
        수동으로 포커스를 조절합니다.
        - focusDirection: 양수는 원거리, 음수는 근거리
        """
        direction = request.json.get("focusDirection")
        logging.info(f"Continuous focus: {direction}")
        sdk.setCameraFocus(1.0, float(direction))
        return {"message": "포커스 값이 설정되었습니다."}

@camera_ns.route('/focus/auto')
class CameraFocusAuto(Resource):
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_focus_auto', description='자동 포커스 실행')
    def post(self):
        """자동 포커스 실행
        
        자동으로 포커스를 맞춥니다.
        """
        logging.info("Auto focus requested")
        sdk.setCameraFocus(1.0)
        return {"message": "AUTO FOCUS"}

@camera_ns.route('/capture-image')
class CameraCaptureImage(Resource):
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_capture_image', description='이미지 캡처')
    def post(self):
        """이미지 캡처
        
        현재 화면을 이미지로 캡처합니다.
        """
        logging.info("Image capture requested")
        sdk.setPayloadCameraCaptureImage(0)
        return {"message": "이미지 캡처가 실행되었습니다."}

@camera_ns.route('/stop-capture')
class CameraStopCapture(Resource):
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_stop_capture', description='이미지 캡처 중지')
    def post(self):
        """이미지 캡처 중지
        
        진행 중인 이미지 캡처를 중지합니다.
        """
        logging.info("Stop image capture requested")
        sdk.setPayloadCameraStopImage()
        return {"message": "이미지 캡처가 중지되었습니다."}

@camera_ns.route('/start-record')
class CameraStartRecord(Resource):
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_start_record', description='비디오 녹화 시작')
    def post(self):
        """비디오 녹화 시작
        
        비디오 녹화를 시작합니다.
        """
        logging.info("Start record requested")
        sdk.setPayloadCameraRecordVideoStart()
        return {"message": "비디오 녹화가 시작되었습니다."}

@camera_ns.route('/stop-record')
class CameraStopRecord(Resource):
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_stop_record', description='비디오 녹화 중지')
    def post(self):
        """비디오 녹화 중지
        
        진행 중인 비디오 녹화를 중지합니다.
        """
        logging.info("Stop record requested")
        sdk.setPayloadCameraRecordVideoStop()
        return {"message": "비디오 녹화가 중지되었습니다."}

@camera_ns.route('/set-ffc-mode')
class CameraSetFFCMode(Resource):
    @camera_ns.expect(ffc_mode_model)
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_set_ffc_mode', description='FFC 모드 설정')
    def post(self):
        """FFC(Non-uniformity Correction) 모드 설정
        
        적외선 센서의 균일성 보정 모드를 설정합니다.
        - ffcMode: 0 (Manual), 1 (Auto)
        """
        mode = request.json.get("ffcMode")
        logging.info(f"Set FFC mode: {mode}")
        sdk.setPayloadCameraFFCMode(int(mode))
        return {"message": "FFC 모드가 설정되었습니다."}

@camera_ns.route('/trigger-ffc')
class CameraTriggerFFC(Resource):
    @camera_ns.marshal_with(success_response)
    @camera_ns.doc('camera_trigger_ffc', description='FFC 트리거 실행')
    def post(self):
        """FFC 트리거 실행
        
        적외선 센서의 균일성 보정을 수동으로 실행합니다.
        """
        logging.info("FFC trigger requested")
        sdk.setPayloadCameraFFCTrigg()
        return {"message": "FFC가 트리거되었습니다."}

# ======================== 짐벌 API ========================
@gimbal_ns.route('/set-mode')
class GimbalSetMode(Resource):
    @gimbal_ns.expect(gimbal_mode_model)
    @gimbal_ns.marshal_with(success_response)
    @gimbal_ns.doc('gimbal_set_mode', description='짐벌 모드 설정')
    def post(self):
        """짐벌 모드 설정
        
        짐벌의 동작 모드를 변경합니다.
        - gimbalSetMode: 0 (Lock), 1 (Follow), 2 (FPV)
        """
        mode = request.json.get("gimbalSetMode")
        logging.info(f"Set gimbal mode: {mode}")
        sdk.setPayloadGimbalParamByID("GIMBAL_MODE", float(mode))
        return {"message": "모드가 설정되었습니다."}

@gimbal_ns.route('/positionMove')
class GimbalPositionMove(Resource):
    @gimbal_ns.expect(gimbal_position_model)
    @gimbal_ns.marshal_with(success_response)
    @gimbal_ns.doc('gimbal_position_move', description='짐벌 위치 이동')
    def post(self):
        """짐벌 위치 이동
        
        특정 각도로 짐벌을 이동시킵니다.
        - yaw: Yaw 각도 (-180 ~ 180)
        - pitch: Pitch 각도 (-90 ~ 90) 
        - roll: Roll 각도 (-180 ~ 180)
        """
        yaw = request.json.get("yaw")
        pitch = request.json.get("pitch")
        roll = request.json.get("roll")
        sdk.setGimbalSpeed(float(pitch), float(roll), float(yaw), 1)
        return {"message": "짐벌 이동이 시작되었습니다."}

@gimbal_ns.route('/continuousMove')
class GimbalContinuousMove(Resource):
    @gimbal_ns.expect(gimbal_continuous_model)
    @gimbal_ns.marshal_with(success_response)
    @gimbal_ns.doc('gimbal_continuous_move', description='짐벌 연속 이동')
    def post(self):
        """짐벌 연속 이동
        
        지속적으로 짐벌을 회전시킵니다. 모든 값이 0이면 정지합니다.
        - yaw: Yaw 속도 (-100 ~ 100)
        - pitch: Pitch 속도 (-100 ~ 100)
        - roll: Roll 속도 (-100 ~ 100)
        """
        yaw = float(request.json.get("yaw", 0))
        pitch = float(request.json.get("pitch", 0))
        roll = float(request.json.get("roll", 0))
        logging.info(f"Gimbal continuous move - yaw:{yaw}, pitch:{pitch}, roll:{roll}")
        
        sdk.setGimbalSpeed(pitch, roll, yaw, input_mode_t.INPUT_SPEED)
        if yaw == 0.0 and pitch == 0.0 and roll == 0.0:
            message = "짐벌 이동이 중지되었습니다."
        else:
            message = "짐벌 이동이 시작되었습니다."
        return {"message": message}

@gimbal_ns.route('/stop')
class GimbalStop(Resource):
    @gimbal_ns.marshal_with(success_response)
    @gimbal_ns.doc('gimbal_stop', description='짐벌 이동 중지')
    def post(self):
        """짐벌 이동 중지
        
        현재 진행 중인 모든 짐벌 이동을 중지합니다.
        """
        sdk.setGimbalSpeed(0, 0, 0, input_mode_t.INPUT_SPEED)
        return {"message": "Gimbal movement stopped"}

@gimbal_ns.route('/set-rc-mode')
class GimbalSetRCMode(Resource):
    @gimbal_ns.expect(rc_mode_model)
    @gimbal_ns.marshal_with(success_response)
    @gimbal_ns.response(400, 'Invalid RC mode', error_response)
    @gimbal_ns.doc('gimbal_set_rc_mode', description='짐벌 RC 모드 설정')
    def post(self):
        """짐벌 RC 모드 설정
        
        짐벌의 원격 제어 모드를 변경합니다.
        - rcMode: 0 (Standard), 1 (Gremsy)
        """
        mode = request.json.get("rcMode")
        if mode not in [payload_camera_rc_mode.PAYLOAD_CAMERA_RC_MODE_STANDARD, 
                       payload_camera_rc_mode.PAYLOAD_CAMERA_RC_MODE_GREMSY]:
            return {"error": "Invalid RC mode"}, 400
        sdk.setPayloadCameraParam(PAYLOAD_CAMERA_RC_MODE, int(mode), param_type.PARAM_TYPE_UINT32)
        return {"message": f"Gimbal RC 모드({mode})가 설정되었습니다."}

@gimbal_ns.route('/calib-gyro')
class GimbalCalibGyro(Resource):
    @gimbal_ns.marshal_with(success_response)
    @gimbal_ns.doc('gimbal_calib_gyro', description='자이로 캘리브레이션')
    def post(self):
        """자이로 캘리브레이션
        
        짐벌의 자이로스코프 센서를 캘리브레이션합니다.
        """
        logging.info("Gimbal gyro calibration requested")
        sdk.sendPayloadGimbalCalibGyro()
        return {"message": "자이로 캘리브레이션이 시작되었습니다."}

@gimbal_ns.route('/calib-accel')
class GimbalCalibAccel(Resource):
    @gimbal_ns.marshal_with(success_response)
    @gimbal_ns.doc('gimbal_calib_accel', description='가속도 캘리브레이션')
    def post(self):
        """가속도 캘리브레이션
        
        짐벌의 가속도 센서를 캘리브레이션합니다.
        """
        logging.info("Gimbal accel calibration requested")
        sdk.sendPayloadGimbalCalibAccel()
        return {"message": "가속도 캘리브레이션이 시작되었습니다."}

@gimbal_ns.route('/calib-motor')
class GimbalCalibMotor(Resource):
    @gimbal_ns.marshal_with(success_response)
    @gimbal_ns.doc('gimbal_calib_motor', description='모터 캘리브레이션')
    def post(self):
        """모터 캘리브레이션
        
        짐벌의 모터를 캘리브레이션합니다.
        """
        logging.info("Gimbal motor calibration requested")
        sdk.sendPayloadGimbalCalibMotor()
        return {"message": "모터 캘리브레이션이 시작되었습니다."}

@gimbal_ns.route('/search-home')
class GimbalSearchHome(Resource):
    @gimbal_ns.marshal_with(success_response)
    @gimbal_ns.doc('gimbal_search_home', description='홈 위치 탐색')
    def post(self):
        """홈 위치 탐색
        
        짐벌의 홈 위치를 탐색하고 이동합니다.
        """
        logging.info("Gimbal home search requested")
        sdk.sendPayloadGimbalSearchHome()
        return {"message": "홈 위치 탐색이 시작되었습니다."}

@gimbal_ns.route('/auto-tune')
class GimbalAutoTune(Resource):
    @gimbal_ns.expect(auto_tune_model)
    @gimbal_ns.marshal_with(success_response)
    @gimbal_ns.doc('gimbal_auto_tune', description='오토 튠')
    def post(self):
        """오토 튜닝
        
        짐벌의 PID 파라미터를 자동으로 조정합니다.
        - status: true (시작), false (중지)
        """
        status = request.json.get("status")
        logging.info(f"Gimbal auto tune: {status}")
        sdk.sendPayloadGimbalAutoTune(bool(status))
        return {"message": "오토 튠이 실행되었습니다."}

if __name__ == "__main__":
    # 환경변수에서 포트 읽기 (기본값: 8000)
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting Flask app with Swagger UI on port {port}")
    print(f"Swagger UI available at: http://localhost:{port}/swagger/")
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    app.run(host="0.0.0.0", port=port, debug=True)