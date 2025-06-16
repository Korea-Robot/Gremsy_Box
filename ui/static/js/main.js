class GremsyController {
    constructor() {
        this.currentSpeed = 10;
        this.isMoving = false;
        this.moveInterval = null;
        this.currentStreamType = 'hls';
        this.hls = null;
        this.webrtcPc = null;
        this.init();
    }

    init() {
        this.checkConnectionStatus();
        this.setupEventListeners();
        this.initializeStream();
        this.log('시스템 초기화 완료');
    }

    setupEventListeners() {
        // 키보드 이벤트
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        document.addEventListener('keyup', (e) => this.handleKeyUp(e));
        
        // 마우스 이벤트 (터치 지원)
        document.addEventListener('touchstart', (e) => e.preventDefault());
    }

    async initializeStream() {
        // HLS 스트림 초기화
        await this.initHLSStream();
        
        // 5초 후 WebRTC 초기화 시도
        setTimeout(() => {
            this.initWebRTCStream();
        }, 5000);
    }

    async initHLSStream() {
        const video = document.getElementById('hls-player');
        const hlsUrl = `http://${window.location.hostname}:8888/gremsy/index.m3u8`;
        
        if (Hls.isSupported()) {
            this.hls = new Hls({
                enableWorker: false,
                lowLatencyMode: true,
                backBufferLength: 90
            });
            
            this.hls.loadSource(hlsUrl);
            this.hls.attachMedia(video);
            
            this.hls.on(Hls.Events.MANIFEST_PARSED, () => {
                this.log('HLS 스트림 연결 성공');
                this.hideStreamPlaceholder();
            });
            
            this.hls.on(Hls.Events.ERROR, (event, data) => {
                this.log(`HLS 오류: ${data.type} - ${data.details}`, 'error');
            });
            
        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
            // Safari native HLS support
            video.src = hlsUrl;
            video.addEventListener('loadedmetadata', () => {
                this.log('네이티브 HLS 스트림 연결 성공');
                this.hideStreamPlaceholder();
            });
        } else {
            this.log('HLS를 지원하지 않는 브라우저입니다', 'error');
        }
    }

    async initWebRTCStream() {
        try {
            // WebRTC 구현은 복잡하므로 우선 iframe으로 대체
            const webrtcPlayer = document.getElementById('webrtc-player');
            const webrtcContainer = webrtcPlayer.parentElement;
            
            // iframe 생성 (MediaMTX WebRTC 페이지)
            const iframe = document.createElement('iframe');
            iframe.id = 'webrtc-iframe';
            iframe.className = 'video-player';
            iframe.src = `http://${window.location.hostname}:8889/gremsy`;
            iframe.style.width = '100%';
            iframe.style.height = '450px';
            iframe.style.border = 'none';
            iframe.style.borderRadius = '10px';
            
            webrtcContainer.insertBefore(iframe, webrtcPlayer);
            webrtcPlayer.remove();
            
            this.log('WebRTC iframe 초기화 완료');
        } catch (error) {
            this.log(`WebRTC 초기화 오류: ${error.message}`, 'error');
        }
    }

    switchStream(type) {
        const hlsPlayer = document.getElementById('hls-player');
        const webrtcPlayer = document.getElementById('webrtc-iframe') || document.getElementById('webrtc-player');
        const tabs = document.querySelectorAll('.tab-btn');
        
        // 탭 스타일 업데이트
        tabs.forEach(tab => tab.classList.remove('active'));
        event.target.classList.add('active');
        
        // 플레이어 전환
        if (type === 'hls') {
            hlsPlayer.classList.add('active');
            webrtcPlayer.classList.remove('active');
            this.currentStreamType = 'hls';
            this.log('HLS 스트림으로 전환');
        } else {
            hlsPlayer.classList.remove('active');
            webrtcPlayer.classList.add('active');
            this.currentStreamType = 'webrtc';
            this.log('WebRTC 스트림으로 전환');
        }
    }

    hideStreamPlaceholder() {
        const placeholder = document.getElementById('stream-placeholder');
        if (placeholder) {
            placeholder.style.display = 'none';
        }
    }

    refreshStream() {
        if (this.currentStreamType === 'hls') {
            this.refreshHLSStream();
        } else {
            this.refreshWebRTCStream();
        }
    }

    refreshHLSStream() {
        if (this.hls) {
            this.hls.destroy();
        }
        this.initHLSStream();
        this.log('HLS 스트림 새로고침');
    }

    refreshWebRTCStream() {
        const iframe = document.getElementById('webrtc-iframe');
        if (iframe) {
            iframe.src = iframe.src;
        }
        this.log('WebRTC 스트림 새로고침');
    }

    openExternalPlayer() {
        const urls = {
            hls: `http://${window.location.hostname}:8888/gremsy/index.m3u8`,
            rtsp: `rtsp://${window.location.hostname}:8554/gremsy`,
            webrtc: `http://${window.location.hostname}:8889/gremsy`
        };
        
        const message = `외부 플레이어 URL:\n\n` +
                       `HLS: ${urls.hls}\n` +
                       `RTSP: ${urls.rtsp}\n` +
                       `WebRTC: ${urls.webrtc}\n\n` +
                       `VLC, MPV, OBS 등에서 사용 가능합니다.`;
        
        alert(message);
        this.log('외부 플레이어 URL 표시');
    }

    async checkConnectionStatus() {
        try {
            const response = await fetch('/api/stream/status');
            const data = await response.json();
            
            const statusElement = document.getElementById('connection-status');
            if (data.success) {
                statusElement.textContent = '🟢 온라인';
                statusElement.className = 'status-indicator online';
                this.log('MediaMTX 연결 확인됨');
            } else {
                throw new Error('MediaMTX 응답 없음');
            }
        } catch (error) {
            const statusElement = document.getElementById('connection-status');
            statusElement.textContent = '🔴 오프라인';
            statusElement.className = 'status-indicator offline';
            this.log(`연결 오류: ${error.message}`, 'error');
        }
    }

    handleKeyDown(event) {
        if (this.isMoving) return;

        switch(event.key) {
            case 'ArrowUp':
            case 'w':
            case 'W':
                this.startMove('pitch', this.currentSpeed);
                break;
            case 'ArrowDown':
            case 's':
            case 'S':
                this.startMove('pitch', -this.currentSpeed);
                break;
            case 'ArrowLeft':
            case 'a':
            case 'A':
                this.startMove('yaw', -this.currentSpeed);
                break;
            case 'ArrowRight':
            case 'd':
            case 'D':
                this.startMove('yaw', this.currentSpeed);
                break;
            case ' ':
                event.preventDefault();
                this.stopMove();
                break;
        }
    }

    handleKeyUp(event) {
        switch(event.key) {
            case 'ArrowUp':
            case 'ArrowDown':
            case 'ArrowLeft':
            case 'ArrowRight':
            case 'w':
            case 'W':
            case 's':
            case 'S':
            case 'a':
            case 'A':
            case 'd':
            case 'D':
                this.stopMove();
                break;
        }
    }

    async startMove(axis, speed) {
        if (this.isMoving) return;
        
        this.isMoving = true;
        const moveData = { yaw: 0, pitch: 0, roll: 0 };
        moveData[axis] = speed;

        try {
            const response = await fetch('/api/gimbal/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(moveData)
            });

            const result = await response.json();
            if (result.success) {
                this.log(`짐벌 이동 시작: ${axis} ${speed}°/s`);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.log(`이동 오류: ${error.message}`, 'error');
            this.isMoving = false;
        }
    }

    async stopMove() {
        if (!this.isMoving) return;
        
        try {
            const response = await fetch('/api/gimbal/stop', {
                method: 'POST'
            });

            const result = await response.json();
            if (result.success) {
                this.log('짐벌 정지');
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.log(`정지 오류: ${error.message}`, 'error');
        } finally {
            this.isMoving = false;
        }
    }

    async changeIRPalette(palette) {
        try {
            const response = await fetch('/api/camera/ir-palette', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ irPalette: parseInt(palette) })
            });

            const result = await response.json();
            if (result.success) {
                this.log(`IR 팔레트 변경: ${palette}`);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.log(`IR 팔레트 변경 오류: ${error.message}`, 'error');
        }
    }

    async changeViewSrc(viewSrc) {
        try {
            const response = await fetch('/api/camera/view-src', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ viewSrc: parseInt(viewSrc) })
            });

            const result = await response.json();
            if (result.success) {
                this.log(`뷰소스 변경: ${viewSrc}`);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.log(`뷰소스 변경 오류: ${error.message}`, 'error');
        }
    }

    updateSpeed(speed) {
        this.currentSpeed = parseInt(speed);
        document.getElementById('speed-value').textContent = speed;
        this.log(`이동 속도 변경: ${speed}°/s`);
    }

    refreshStream() {
        const video = document.getElementById('video-player');
        const currentSrc = video.src;
        video.src = '';
        setTimeout(() => {
            video.src = currentSrc;
            video.load();
        }, 100);
        this.log('스트림 새로고침');
    }

    log(message, type = 'info') {
        const logElement = document.getElementById('activity-log');
        const timestamp = new Date().toLocaleTimeString();
        const logType = type === 'error' ? '❌' : '✅';
        
        const logEntry = `[${timestamp}] ${logType} ${message}\n`;
        logElement.textContent += logEntry;
        logElement.scrollTop = logElement.scrollHeight;
    }
}

// 전역 함수들
let controller;

window.addEventListener('DOMContentLoaded', () => {
    controller = new GremsyController();
});

function startMove(axis, speed) {
    controller.startMove(axis, speed);
}

function stopMove() {
    controller.stopMove();
}

function changeIRPalette(palette) {
    controller.changeIRPalette(palette);
}

function changeViewSrc(viewSrc) {
    controller.changeViewSrc(viewSrc);
}

function updateSpeed(speed) {
    controller.updateSpeed(speed);
}

function refreshStream() {
    controller.refreshStream();
}

function switchStream(type) {
    controller.switchStream(type);
}

function openExternalPlayer() {
    controller.openExternalPlayer();
}