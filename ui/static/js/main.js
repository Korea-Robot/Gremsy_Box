// 전역 변수
let gimbalMoveInterval = null;
let zoomInterval = null;
let currentYaw = 0;
let currentPitch = 0;

// 초기화
document.addEventListener('DOMContentLoaded', function() {
    addLog('시스템 초기화 완료');
    checkStreamConnection();
    setupKeyboardControls();
    updateStatus('시스템 준비 완료');
});

// 스트림 연결 확인
function checkStreamConnection() {
    const iframe = document.getElementById('webrtcStream');
    const video = document.getElementById('videoStream');
    
    if (iframe) {
        iframe.onload = function() {
            addLog('WebRTC 스트림 연결 성공');
            updateStatus('스트림 연결됨');
        };
        
        iframe.onerror = function() {
            addLog('WebRTC 스트림 연결 실패 - 대체 방법 시도');
            iframe.style.display = 'none';
            video.style.display = 'block';
            // 대체 스트림 URL 시도
            tryAlternativeStream();
        };
    }
}

// 대체 스트림 시도
function tryAlternativeStream() {
    const video = document.getElementById('videoStream');
    const streamUrls = [
        `http://192.168.168.105:8889/gremsy/`,
        `http://192.168.168.105:8889/gremsy/stream`,
        `http://192.168.168.105:8554/gremsy`
    ];
    
    let urlIndex = 0;
    
    function tryNextUrl() {
        if (urlIndex < streamUrls.length) {
            video.src = streamUrls[urlIndex];
            addLog(`대체 스트림 시도: ${streamUrls[urlIndex]}`);
            urlIndex++;
        } else {
            addLog('모든 스트림 연결 실패');
            updateStatus('스트림 연결 실패');
        }
    }
    
    video.onerror = tryNextUrl;
    video.onloadstart = function() {
        addLog('비디오 스트림 로드 시작');
    };
    
    tryNextUrl();
}

// ======== 짐벌 제어 함수들 ========

// 연속 짐벌 이동 시작
function startGimbalMove(yaw, pitch) {
    // 기존 인터벌이 있다면 정리
    if (gimbalMoveInterval) {
        clearInterval(gimbalMoveInterval);
    }
    
    // 즉시 첫 번째 명령 전송
    sendGimbalMove(yaw, pitch);
    
    // 연속 명령을 위한 인터벌 설정 (100ms마다)
    gimbalMoveInterval = setInterval(() => {
        sendGimbalMove(yaw, pitch);
    }, 100);
    
    addLog(`짐벌 이동 시작: Yaw=${yaw}, Pitch=${pitch}`);
}

// 짐벌 이동 API 호출
function sendGimbalMove(yaw, pitch) {
    fetch('/api/gimbal/continuous-move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            yaw: yaw,
            pitch: pitch,
            roll: 0
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'error') {
            addLog(`짐벌 제어 오류: ${data.message}`);
        }
    })
    .catch(error => {
        addLog(`짐벌 제어 실패: ${error.message}`);
    });
}

// 짐벌 정지
function stopGimbal() {
    if (gimbalMoveInterval) {
        clearInterval(gimbalMoveInterval);
        gimbalMoveInterval = null;
    }
    
    fetch('/api/gimbal/stop', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        addLog(data.message);
        if (data.status === 'success') {
            updateStatus('짐벌 정지');
        }
    })
    .catch(error => {
        addLog(`짐벌 정지 실패: ${error.message}`);
    });
}

// 짐벌 리셋
function resetGimbal() {
    stopGimbal(); // 먼저 정지
    
    fetch('/api/gimbal/reset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        addLog(data.message);
        if (data.status === 'success') {
            // 슬라이더도 0으로 리셋
            document.getElementById('yawSlider').value = 0;
            document.getElementById('pitchSlider').value = 0;
            updateGimbalValue('yaw', 0);
            updateGimbalValue('pitch', 0);
            updateStatus('짐벌 리셋 완료');
        }
    })
    .catch(error => {
        addLog(`짐벌 리셋 실패: ${error.message}`);
    });
}

// 슬라이더 값 업데이트
function updateGimbalValue(axis, value) {
    const displayValue = document.getElementById(axis + 'Value');
    displayValue.textContent = value + '°';
    
    if (axis === 'yaw') {
        currentYaw = parseFloat(value);
    } else if (axis === 'pitch') {
        currentPitch = parseFloat(value);
    }
}

// 정밀 위치 적용
function applyGimbalPosition() {
    fetch('/api/gimbal/position-move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            yaw: currentYaw,
            pitch: currentPitch,
            roll: 0
        })
    })
    .then(response => response.json())
    .then(data => {
        addLog(data.message);
        if (data.status === 'success') {
            updateStatus(`위치 적용: Yaw=${currentYaw}°, Pitch=${currentPitch}°`);
        }
    })
    .catch(error => {
        addLog(`위치 적용 실패: ${error.message}`);
    });
}

// ======== 카메라 제어 함수들 ========

// 뷰 소스 변경
function changeViewSource(viewSrc) {
    fetch('/api/camera/view-source', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({viewSrc: viewSrc})
    })
    .then(response => response.json())
    .then(data => {
        addLog(data.message);
        if (data.status === 'success') {
            const sources = ['통합', 'EO', 'IR', '전환', '동기화'];
            updateStatus(`뷰 소스: ${sources[viewSrc]}`);
        }
    })
    .catch(error => {
        addLog(`뷰 소스 변경 실패: ${error.message}`);
    });
}

// IR 팔레트 변경
function changeIRPalette() {
    const palette = document.getElementById('irPalette').value;
    const paletteName = document.getElementById('irPalette').selectedOptions[0].text;
    
    fetch('/api/camera/ir-palette', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({irPalette: parseInt(palette)})
    })
    .then(response => response.json())
    .then(data => {
        addLog(data.message);
        if (data.status === 'success') {
            updateStatus(`IR 팔레트: ${paletteName}`);
        }
    })
    .catch(error => {
        addLog(`IR 팔레트 변경 실패: ${error.message}`);
    });
}

// 연속 줌 시작
function startZoom(direction) {
    if (zoomInterval) {
        clearInterval(zoomInterval);
    }
    
    // 즉시 첫 번째 줌 명령 전송
    sendZoomCommand(direction);
    
    // 연속 줌을 위한 인터벌 설정
    zoomInterval = setInterval(() => {
        sendZoomCommand(direction);
    }, 100);
    
    addLog(`줌 ${direction > 0 ? '인' : '아웃'} 시작`);
}

// 줌 명령 전송
function sendZoomCommand(direction) {
    fetch('/api/camera/zoom/continuous', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({zoomDirection: direction})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'error') {
            addLog(`줌 제어 오류: ${data.message}`);
        }
    })
    .catch(error => {
        addLog(`줌 제어 실패: ${error.message}`);
    });
}

// 줌 정지
function stopZoom() {
    if (zoomInterval) {
        clearInterval(zoomInterval);
        zoomInterval = null;
    }
    addLog('줌 정지');
}

// 줌 값 업데이트 (슬라이더)
function updateZoomValue(value) {
    document.getElementById('zoomValue').textContent = value + '%';
}

// 줌 레인지 설정
function setZoomRange(percentage) {
    fetch('/api/camera/zoom/range', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({zoomPercentage: parseInt(percentage)})
    })
    .then(response => response.json())
    .then(data => {
        addLog(data.message);
        if (data.status === 'success') {
            updateStatus(`줌 레벨: ${percentage}%`);
        }
    })
    .catch(error => {
        addLog(`줌 레인지 설정 실패: ${error.message}`);
    });
}

// OSD 모드 설정
function setOSDMode(mode) {
    fetch('/api/camera/osd-mode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({osdMode: mode})
    })
    .then(response => response.json())
    .then(data => {
        addLog(data.message);
        if (data.status === 'success') {
            const modes = ['끄기', '디버그', '상태정보'];
            updateStatus(`OSD 모드: ${modes[mode]}`);
        }
    })
    .catch(error => {
        addLog(`OSD 모드 설정 실패: ${error.message}`);
    });
}

// ======== 키보드 제어 ========
function setupKeyboardControls() {
    document.addEventListener('keydown', function(event) {
        // 키가 이미 눌려있다면 무시 (연속 입력 방지)
        if (event.repeat) return;
        
        switch(event.key.toLowerCase()) {
            case 'w':
            case 'arrowup':
                event.preventDefault();
                startGimbalMove(0, -10);
                break;
            case 's':
            case 'arrowdown':
                event.preventDefault();
                startGimbalMove(0, 10);
                break;
            case 'a':
            case 'arrowleft':
                event.preventDefault();
                startGimbalMove(-10, 0);
                break;
            case 'd':
            case 'arrowright':
                event.preventDefault();
                startGimbalMove(10, 0);
                break;
            case ' ':
                event.preventDefault();
                stopGimbal();
                break;
            case 'r':
                event.preventDefault();
                resetGimbal();
                break;
            case '=':
            case '+':
                event.preventDefault();
                startZoom(1);
                break;
            case '-':
                event.preventDefault();
                startZoom(-1);
                break;
        }
    });
    
    document.addEventListener('keyup', function(event) {
        switch(event.key.toLowerCase()) {
            case 'w':
            case 's':
            case 'a':
            case 'd':
            case 'arrowup':
            case 'arrowdown':
            case 'arrowleft':
            case 'arrowright':
                event.preventDefault();
                stopGimbal();
                break;
            case '=':
            case '+':
            case '-':
                event.preventDefault();
                stopZoom();
                break;
        }
    });
    
    addLog('키보드 제어 활성화 (WASD/화살표키: 이동, 스페이스: 정지, R: 리셋, +/-: 줌)');
}

// ======== 유틸리티 함수들 ========

// 로그 추가
function addLog(message) {
    const logContainer = document.getElementById('logContainer');
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    
    const timestamp = new Date().toLocaleTimeString();
    logEntry.innerHTML = `<span class="timestamp">[${timestamp}]</span> ${message}`;
    
    logContainer.appendChild(logEntry);
    
    // 로그가 너무 많으면 오래된 것 제거
    const logs = logContainer.querySelectorAll('.log-entry');
    if (logs.length > 50) {
        logs[0].remove();
    }
    
    // 자동 스크롤
    logContainer.scrollTop = logContainer.scrollHeight;
}

// 로그 지우기
function clearLog() {
    const logContainer = document.getElementById('logContainer');
    logContainer.innerHTML = '<div class="log-entry">로그가 지워졌습니다.</div>';
}

// 상태 업데이트
function updateStatus(message) {
    const statusElement = document.getElementById('status');
    statusElement.textContent = message;
    statusElement.className = 'status active';
    
    // 3초 후 기본 상태로 복귀
    setTimeout(() => {
        statusElement.className = 'status';
    }, 3000);
}

// 페이지 언로드시 정리
window.addEventListener('beforeunload', function() {
    if (gimbalMoveInterval) {
        clearInterval(gimbalMoveInterval);
    }
    if (zoomInterval) {
        clearInterval(zoomInterval);
    }
    stopGimbal();
});