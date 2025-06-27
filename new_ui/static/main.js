let pc = null;
let localStream = null;
let flipMode = 3; // 초기값: 플립 끔

// WebRTC 스트림 관련 함수
async function startStream() {
    try {
        const video = document.getElementById('video');
        
        pc = new RTCPeerConnection({
            iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
        });

        pc.ontrack = (event) => {
            video.srcObject = event.streams[0];
            showStatus('스트림 연결됨', 'success');
        };

        pc.oniceconnectionstatechange = () => {
            showStatus(`ICE 연결 상태: ${pc.iceConnectionState}`, 'success');
        };

        // Offer 생성 및 전송
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        const response = await fetch(WEBRTC_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/sdp' },
            body: offer.sdp
        });

        if (response.ok) {
            const answer = await response.text();
            await pc.setRemoteDescription({
                type: 'answer',
                sdp: answer
            });
            showStatus('WebRTC 연결 성공', 'success');
        } else {
            throw new Error('WebRTC 연결 실패');
        }
    } catch (error) {
        showStatus(`스트림 시작 실패: ${error.message}`, 'error');
    }
}

function stopStream() {
    if (pc) {
        pc.close();
        pc = null;
    }
    
    const video = document.getElementById('video');
    video.srcObject = null;
    showStatus('스트림 정지됨', 'success');
}

// 카메라 제어 함수들
async function zoomStep(direction) {
    await sendCameraCommand('zoom-step', { zoomDirection: direction });
}

async function zoomRange(percentage) {
    document.getElementById('zoomValue').textContent = percentage + '%';
    await sendCameraCommand('zoom-range', { zoomPercentage: parseInt(percentage) });
}

async function changeViewSrc(viewSrc) {
    await sendCameraCommand('change-view', { viewSrc: parseInt(viewSrc) });
}

async function setFocusMode(focusMode) {
    await sendCameraCommand('focus-mode', { focusMode: parseInt(focusMode) });
}

async function focusContinuous(direction) {
    await sendCameraCommand('focus-continuous', { focusDirection: direction });
}

async function autoFocus() {
    await sendCameraCommand('focus-auto', {});
}

async function setIrPalette(irPalette) {
    await sendCameraCommand('ir-palette', { irPalette: parseInt(irPalette) });
}

async function setOsdMode(osdMode) {
    await sendCameraCommand('osd-mode', { osdMode: parseInt(osdMode) });
}

async function toggleFlip() {
    flipMode = flipMode === 2 ? 3 : 2;
    await sendCameraCommand('flip-mode', { flipMode: flipMode });
    showStatus(`플립 모드: ${flipMode === 2 ? '켜짐' : '꺼짐'}`, 'success');
}

// 짐벌 제어 함수들
async function setGimbalMode(mode) {
    await sendGimbalCommand('set-mode', { gimbalSetMode: parseInt(mode) });
}

function updateGimbalValues() {
    const yaw = document.getElementById('yawSlider').value;
    const pitch = document.getElementById('pitchSlider').value;
    const roll = document.getElementById('rollSlider').value;
    
    document.getElementById('yawValue').textContent = yaw + '°';
    document.getElementById('pitchValue').textContent = pitch + '°';
    document.getElementById('rollValue').textContent = roll + '°';
}

async function moveGimbalPosition() {
    const yaw = parseFloat(document.getElementById('yawSlider').value);
    const pitch = parseFloat(document.getElementById('pitchSlider').value);
    const roll = parseFloat(document.getElementById('rollSlider').value);
    
    await sendGimbalCommand('position-move', { yaw, pitch, roll });
}

async function stopGimbal() {
    await sendGimbalCommand('move', { yaw: 0, pitch: 0, roll: 0 });
}

// API 통신 함수들
async function sendCameraCommand(action, data) {
    try {
        const response = await fetch(`/api/camera/${action}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showStatus(`카메라 ${action} 성공`, 'success');
        } else {
            showStatus(`카메라 ${action} 실패: ${result.error}`, 'error');
        }
    } catch (error) {
        showStatus(`카메라 ${action} 오류: ${error.message}`, 'error');
    }
}

async function sendGimbalCommand(action, data) {
    try {
        const response = await fetch(`/api/gimbal/${action}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showStatus(`짐벌 ${action} 성공`, 'success');
        } else {
            showStatus(`짐벌 ${action} 실패: ${result.error}`, 'error');
        }
    } catch (error) {
        showStatus(`짐벌 ${action} 오류: ${error.message}`, 'error');
    }
}

// 상태 메시지 표시
function showStatus(message, type) {
    const status = document.getElementById('status');
    const timestamp = new Date().toLocaleTimeString();
    status.innerHTML = `<div class="${type}"><strong>[${timestamp}]</strong> ${message}</div>` + status.innerHTML;
    
    // 최대 10개의 메시지만 유지
    const messages = status.children;
    if (messages.length > 10) {
        status.removeChild(messages[messages.length - 1]);
    }
}

// 키보드 단축키
document.addEventListener('keydown', (event) => {
    switch(event.key) {
        case 'ArrowUp':
            event.preventDefault();
            zoomStep(1);
            break;
        case 'ArrowDown':
            event.preventDefault();
            zoomStep(-1);
            break;
        case ' ':
            event.preventDefault();
            autoFocus();
            break;
    }
});

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    showStatus('VIO 카메라 & 짐벌 제어 시스템 준비됨', 'success');
    
    // 슬라이더 초기값 설정
    updateGimbalValues();
});