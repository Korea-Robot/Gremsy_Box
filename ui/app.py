from flask import Flask, render_template, request, jsonify
import os, requests

app = Flask(__name__)

# .env 또는 docker-compose.yml 에 설정한 값 읽어오기
GREMSY_API_BASE = os.environ.get('GREMSY_API_BASE', 'http://127.0.0.1:8000')

# 메인(UI) 페이지
@app.route('/')
def index():
    return render_template('index.html')

# Gimbal 제어 (continuousMove, stop)
@app.route('/gimbal/continuousMove', methods=['POST'])
@app.route('/gimbal/stop', methods=['POST'])
# Camera 제어 (IR palette, view source)
@app.route('/camera/set-ir-palette', methods=['POST'])
@app.route('/camera/change-view-src', methods=['POST'])
def proxy_control():
    # 원래 요청 경로와 동일하게 Gremsy API로 전달
    target_url = f"{GREMSY_API_BASE}{request.path}"
    resp = requests.post(
        target_url,
        json=request.get_json() or {},
        timeout=3
    )
    return (resp.text, resp.status_code, resp.headers.items())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('UI_PORT', 7777)))
