// WebRTC 설정
let pc = null;
let ws = null;
const video = document.getElementById('webrtc-video');
const connectionStatus = document.getElementById('connection-status');
const zoomRange = document.getElementById('zoom-range');
const zoomValue = document.getElementById('zoom-value');

// 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializeWebRTC();
    setupEventListeners();
    updateConnectionStatus(false);
});

// WebRTC 초기화
function initializeWebRTC() {
    try {
        const url = new URL(window.WEBRTC_URL);
        const wsUrl = `ws://${url.host}${url.pathname}ws`;
        
        ws = new WebSocket(wsUrl);
        
        ws.onopen = function() {
            console.log('WebSocket 연결됨');
            setupWebRTC();
        };
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            handleWebRTCMessage(data);
        };
        
        ws.onclose = function() {
            console.log('WebSocket 연결 해제됨');
            updateConnectionStatus(false);
            setTimeout(initializeWebRTC, 3000); // 재연결 시도
        };
        
        ws.onerror = function(error) {
            console.error('WebSocket 오류:', error);
            updateConnectionStatus(false);
        };
        
    } catch (error) {
        console.error('WebRTC 초기화 오류:', error);
        updateConnectionStatus(false);
    }
}

function setupWebRTC() {
    pc = new RTCPeerConnection({
        iceServers: [{urls: 'stun:stun.l.google.com:19302'}]
    });
    
    pc.ontrack = function(event) {
        video.srcObject = event.streams[0];
        updateConnectionStatus(true);
    };
    
    pc.onicecandidate = function(event) {
        if (event.candidate) {
            ws.send(JSON.stringify({
                type: 'candidate',
                candidate: event.candidate
            }));
        }
    };
    
    // Offer 생성
    pc.createOffer().then(function(offer) {
        return pc.setLocalDescription(offer);
    }).then(function() {
        ws.send(JSON.stringify({
            type: 'offer',
            sdp: pc.localDescription
        }));
    }).catch(function(error) {
        console.error('Offer 생성 오류:', error);
    });
}

function handleWebRTCMessage(data) {
    if (data.type === 'answer') {
        pc.setRemoteDescription(new RTCSessionDescription(data.sdp));
    } else if (data.type === 'candidate') {
        pc.addIceCandidate(new RTCIceCandidate(data.candidate));
    }
}

function updateConnectionStatus(connected) {
    if (connected) {
        connectionStatus.textContent = '🟢 연결됨';
        connectionStatus.className = 'connected';
    } else {
        connectionStatus.textContent = '🔴 연결 끊김';
        connectionStatus.className = 'disconnected';
    }
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 줌 슬라이더
    zoomRange.addEventListener('input', function() {
        zoomValue.textContent = this.value + '%';
    });
    
    // 짐벌 이동 버튼들
    document.querySelectorAll('.move-btn').forEach(btn => {
        btn.addEventListener('mousedown', function() {
            const yaw = parseFloat(this.dataset.yaw) || 0;
            const pitch = parseFloat(this.dataset.pitch) || 0;
            const roll = parseFloat(this.dataset.roll) || 0;
            moveGimbal(yaw, pitch, roll);
        });
        
        btn.addEventListener('mouseup', stopGimbal);
        btn.addEventListener('mouseleave', stopGimbal);
    });
}

// API 호출 함수
async function apiCall(endpoint, data = {}) {
    try {
        const response = await fetch(`${window.API_BASE}/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log(`✅ ${endpoint} 성공:`, result);
        } else {
            console.error(`❌ ${endpoint} 실패:`, result);
        }
        
        return result;
    } catch (error) {
        console.error(`🔥 API 호출 오류 (${endpoint}):`, error);
        return { success: false, error: error.message };
    }
}

// 카메라 제어 함수들
function cameraZoomStep(direction) {
    apiCall('camera/zoom/step', { zoomDirection: direction });
}

function cameraZoomContinuous(direction) {
    apiCall('camera/zoom/continuous', { zoomDirection: direction });
}

function cameraZoomRange(percentage) {
    apiCall('camera/zoom/range', { zoomPercentage: parseInt(percentage) });
}

function changeViewSource(viewSrc) {
    apiCall('camera/change-view-src', { viewSrc: parseInt(viewSrc) });
}

function setFocusMode(mode) {
    apiCall('camera/focus/set-mode', { focusMode: parseInt(mode) });
}

function focusContinuous(direction) {
    apiCall('camera/focus/continuous', { focusDirection: parseInt(direction) });
}

function autoFocus() {
    apiCall('camera/focus/auto');
}

function setIRPalette(palette) {
    apiCall('camera/set-ir-palette', { irPalette: parseInt(palette) });
}

function setOSDMode(mode) {
    apiCall('camera/set-osd-mode', { osdMode: parseInt(mode) });
}

function setFlipMode(mode) {
    apiCall('camera/set-flip-mode', { flipMode: parseInt(mode) });
}

// 짐벌 제어 함수들
function setGimbalMode(mode) {
    apiCall('gimbal/set-mode', { gimbalSetMode: parseInt(mode) });
}

function moveGimbalPosition() {
    const yaw = parseFloat(document.getElementById('yaw').value) || 0;
    const pitch = parseFloat(document.getElementById('pitch').value) || 0;
    const roll = parseFloat(document.getElementById('roll').value) || 0;
    
    apiCall('gimbal/positionMove', { yaw, pitch, roll });
}

function moveGimbal(yaw, pitch, roll) {
    apiCall('gimbal/move', { yaw, pitch, roll });
}

function stopGimbal() {
    apiCall('gimbal/move', { yaw: 0, pitch: 0, roll: 0 });
}

// 키보드 단축키
document.addEventListener('keydown', function(e) {
    switch(e.code) {
        case 'ArrowUp':
            e.preventDefault();
            moveGimbal(5, 0, 0);
            break;
        case 'ArrowDown':
            e.preventDefault();
            moveGimbal(-5, 0, 0);
            break;
        case 'ArrowLeft':
            e.preventDefault();
            moveGimbal(0, -5, 0);
            break;
        case 'ArrowRight':
            e.preventDefault();
            moveGimbal(0, 5, 0);
            break;
        case 'Space':
            e.preventDefault();
            stopGimbal();
            break;
        case 'Equal':
            e.preventDefault();
            cameraZoomStep(1);
            break;
        case 'Minus':
            e.preventDefault();
            cameraZoomStep(-1);
            break;
    }
});

document.addEventListener('keyup', function(e) {
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) {
        stopGimbal();
    }
});