// 전역 변수
let gimbalMoveInterval = null;
let zoomInterval = null;
let currentYaw = 0;
let currentPitch = 0;

// DOM 로드 완료 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializeSystem();
    setupEventListeners();
});

// 시스템 초기화
function initializeSystem() {
    addLog('시스템이 초기화되었습니다.', 'success');
    updateStatus('시스템 준비됨');
    
    // 슬라이더 초기값 설정
    updateSliderValues();
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 줌 슬라이더 이벤트
    const zoomRange = document.getElementById('zoomRange');
    zoomRange.addEventListener('input', function() {
        document.getElementById('zoomValue').textContent = this.value + '%';
    });
    
    // 짐벌 슬라이더 이벤트
    const yawSlider = document.getElementById('yawSlider');
    const pitchSlider = document.getElementById('pitchSlider');
    
    yawSlider.addEventListener('input', function() {
        currentYaw = parseFloat(this.value);
        document.getElementById('yawValue').textContent = currentYaw + '°';
    });
    
    pitchSlider.addEventListener('input', function() {
        currentPitch = parseFloat(this.value);
        document.getElementById('pitchValue').textContent = currentPitch + '°';
    });
}

// 상태 업데이트
function updateStatus(message) {
    const statusElement = document.getElementById('status');
    statusElement.textContent = message;
}

// 로그 추가
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('logContainer');
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    
    const timestamp = new Date().toLocaleTimeString();
    logEntry.textContent = `[${timestamp}] ${message}`;
    
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
    
    // 로그가 너무 많으면 오래된 것 제거
    const logEntries = logContainer.querySelectorAll('.log-entry');
    if (logEntries.length > 100) {
        logEntries[0].remove();
    }
}

// 로그 지우기
function clearLog() {
    const logContainer = document.getElementById('logContainer');
    logContainer.innerHTML = '';
    addLog('로그가 지워졌습니다.', 'info');
}

// 슬라이더 값 업데이트
function updateSliderValues() {
    document.getElementById('yawValue').textContent = currentYaw + '°';
    document.getElementById('pitchValue').textContent = currentPitch + '°';
    document.getElementById('zoomValue').textContent = document.getElementById('zoomRange').value + '%';
}

// API 요청 함수
async function makeAPIRequest(url, data = {}) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            addLog(result.message, 'success');
            return result;
        } else {
            addLog(`오류: ${result.message}`, 'error');
            return null;
        }
    } catch (error) {
        addLog(`네트워크 오류: ${error.message}`, 'error');
        return null;
    }
}

// 카메라 제어 함수들
async function changeViewSource(viewSrc) {
    const viewSources = {
        0: 'EO/IR 통합',
        1: 'EO',
        2: 'IR',
        3: 'IR/EO 전환',
        4: '동기화 뷰'
    };
    
    addLog(`뷰 소스를 ${viewSources[viewSrc]}로 변경 중...`, 'info');
    await makeAPIRequest('/api/camera/view-source', { viewSrc: viewSrc });
}

async function changeIRPalette() {
    const select = document.getElementById('irPalette');
    const irPalette = parseInt(select.value);
    const paletteName = select.options[select.selectedIndex].text;
    
    addLog(`IR 팔레트를 ${paletteName}로 변경 중...`, 'info');
    await makeAPIRequest('/api/camera/ir-palette', { irPalette: irPalette });
}

async function setOSDMode(osdMode) {
    const osdModes = {
        0: '비활성화',
        1: '디버그 모드',
        2: '상태 정보 표시'
    };
    
    addLog(`OSD 모드를 ${osdModes[osdMode]}로 설정 중...`, 'info');
    await makeAPIRequest('/api/camera/osd-mode', { osdMode: osdMode });
}

// 줌 제어 함수들
function startZoom(direction) {
    if (zoomInterval) {
        clearInterval(zoomInterval);
    }
    
    const directionText = direction === 1 ? '인' : '아웃';
    addLog(`줌 ${directionText} 시작`, 'info');
    
    // 즉시 한 번 실행
    makeAPIRequest('/api/camera/zoom/continuous', { zoomDirection: direction });
    
    // 연속 줌을 위한 인터벌 설정
    zoomInterval = setInterval(() => {
        makeAPIRequest('/api/camera/zoom/continuous', { zoomDirection: direction });
    }, 100);
}

function stopZoom() {
    if (zoomInterval) {
        clearInterval(zoomInterval);
        zoomInterval = null;
        addLog('줌 정지', 'info');
        makeAPIRequest('/api/camera/zoom/continuous', { zoomDirection: 0 });
    }
}

async function setZoomRange(percentage) {
    addLog(`줌 레인지를 ${percentage}%로 설정 중...`, 'info');
    await makeAPIRequest('/api/camera/zoom/range', { zoomPercentage: parseInt(percentage) });
}

// 짐벌 제어 함수들
function startGimbalMove(yaw, pitch) {
    if (gimbalMoveInterval) {
        clearInterval(gimbalMoveInterval);
    }
    
    addLog(`짐벌 이동 시작 (Yaw: ${yaw}, Pitch: ${pitch})`, 'info');
    
    // 즉시 한 번 실행
    makeAPIRequest('/api/gimbal/continuous-move', {
        // yaw: yaw,
        // pitch: pitch,
        // roll: 0

        pitch: yaw,
        roll: pitch,
        yaw: roll
    });
    
    // 연속 이동을 위한 인터벌 설정
    gimbalMoveInterval = setInterval(() => {
        makeAPIRequest('/api/gimbal/continuous-move', {
            // yaw: yaw,
            // pitch: pitch,
            // roll: 0

            pitch: yaw,
            roll: 0,
            yaw: roll
        });
    }, 100);
}

function stopGimbal() {
    if (gimbalMoveInterval) {
        clearInterval(gimbalMoveInterval);
        gimbalMoveInterval = null;
        addLog('짐벌 이동 정지', 'info');
        makeAPIRequest('/api/gimbal/stop');
    }
}

async function resetGimbal() {
    addLog('짐벌 리셋 중...', 'info');
    
    // 슬라이더 값도 초기화
    document.getElementById('yawSlider').value = 0;
    document.getElementById('pitchSlider').value = 0;
    currentYaw = 0;
    currentPitch = 0;
    updateSliderValues();
    
    await makeAPIRequest('/api/gimbal/reset');
}

function updateGimbalValue(axis, value) {
    if (axis === 'yaw') {
        currentYaw = parseFloat(value);
        document.getElementById('yawValue').textContent = currentYaw + '°';
    } else if (axis === 'pitch') {
        currentPitch = parseFloat(value);
        document.getElementById('pitchValue').textContent = currentPitch + '°';
    }
}

async function applyGimbalPosition() {
    addLog(`짐벌 위치 적용 중 (Yaw: ${currentYaw}°, Pitch: ${currentPitch}°)`, 'info');
    await makeAPIRequest('/api/gimbal/position-move', {
        // yaw: currentYaw,
        // pitch: currentPitch,
        // roll: 0
        yaw: currentPitch,
        pitch: 0,
        roll: currentYaw
    });
}

// 키보드 단축키 지원
document.addEventListener('keydown', function(event) {
    // 입력 필드에 포커스가 있을 때는 단축키 비활성화
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'SELECT') {
        return;
    }
    
    switch(event.key.toLowerCase()) {
        case 'w':
        case 'arrowup':
            event.preventDefault();
            startGimbalMove(0, -5);
            break;
        case 's':
        case 'arrowdown':
            event.preventDefault();
            startGimbalMove(0, 5);
            break;
        case 'a':
        case 'arrowleft':
            event.preventDefault();
            startGimbalMove(-5, 0);
            break;
        case 'd':
        case 'arrowright':
            event.preventDefault();
            startGimbalMove(5, 0);
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
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'SELECT') {
        return;
    }
    
    switch(event.key.toLowerCase()) {
        case 'w':
        case 's':
        case 'a':
        case 'd':
        case 'arrowup':
        case 'arrowdown':
        case 'arrowleft':
        case 'arrowright':
            stopGimbal();
            break;
        case '=':
        case '+':
        case '-':
            stopZoom();
            break;
    }
});

// 페이지 언로드 시 정리
window.addEventListener('beforeunload', function() {
    if (gimbalMoveInterval) {
        clearInterval(gimbalMoveInterval);
        makeAPIRequest('/api/gimbal/stop');
    }
    if (zoomInterval) {
        clearInterval(zoomInterval);
        makeAPIRequest('/api/camera/zoom/continuous', { zoomDirection: 0 });
    }
});

// 비디오 스트림 오류 처리
document.getElementById('videoStream').addEventListener('error', function() {
    addLog('비디오 스트림 연결 오류', 'error');
    updateStatus('스트림 연결 실패');
});

document.getElementById('videoStream').addEventListener('load', function() {
    addLog('비디오 스트림 연결됨', 'success');
    updateStatus('스트림 연결됨');
});

// 터치 이벤트 지원 (모바일)
function addTouchSupport() {
    const directionButtons = document.querySelectorAll('.dir-btn');
    
    directionButtons.forEach(button => {
        button.addEventListener('touchstart', function(e) {
            e.preventDefault();
            const mouseEvent = new MouseEvent('mousedown', {
                view: window,
                bubbles: true,
                cancelable: true
            });
            button.dispatchEvent(mouseEvent);
        });
        
        button.addEventListener('touchend', function(e) {
            e.preventDefault();
            const mouseEvent = new MouseEvent('mouseup', {
                view: window,
                bubbles: true,
                cancelable: true
            });
            button.dispatchEvent(mouseEvent);
        });
    });
}

// 터치 지원 초기화
addTouchSupport();

// 개발자 도구용 헬퍼 함수들
window.debugAPI = {
    testGimbalMove: (yaw, pitch) => makeAPIRequest('/api/gimbal/continuous-move', { yaw, pitch, roll: 0 }),
    testZoom: (direction) => makeAPIRequest('/api/camera/zoom/continuous', { zoomDirection: direction }),
    testViewSource: (src) => makeAPIRequest('/api/camera/view-source', { viewSrc: src }),
    getLogs: () => document.getElementById('logContainer').innerHTML,
    clearLogs: () => clearLog()
};

console.log('카메라 & 짐벌 제어 시스템이 로드되었습니다.');
console.log('키보드 단축키:');
console.log('  WASD / 화살표 키: 짐벌 이동');
console.log('  스페이스바: 짐벌 정지');
console.log('  R: 짐벌 리셋');
console.log('  +/-: 줌 인/아웃');
console.log('개발자 도구에서 window.debugAPI 객체를 사용하여 API를 테스트할 수 있습니다.');