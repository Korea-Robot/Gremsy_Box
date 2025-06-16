#!/bin/bash

echo "🐳 Docker로 Gremsy Web Controller 시작 중..."

# Docker 및 docker-compose 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose가 설치되지 않았습니다."
    exit 1
fi

# 기존 컨테이너 정리
echo "🧹 기존 컨테이너 정리 중..."
docker-compose down

# 로그 디렉토리 생성
mkdir -p logs

# 컨테이너 빌드 및 실행
echo "🚀 컨테이너 빌드 및 실행 중..."
docker-compose up --build -d

# 상태 확인
echo "📊 컨테이너 상태 확인 중..."
docker-compose ps

echo ""
echo "✅ 시작 완료!"
echo "🌐 웹 접속: http://192.168.168.105:5000"
echo "📺 HLS 스트림: http://192.168.168.105:8888/gremsy/index.m3u8"
echo "🎥 WebRTC 접속: http://192.168.168.105:8889/gremsy"
echo ""
echo "📋 로그 확인: docker-compose logs -f"
echo "🛑 중지: docker-compose down"