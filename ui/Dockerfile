# ui/Dockerfile

FROM python:3.10-slim

# 컨테이너 내부 작업 디렉터리 설정
WORKDIR /app

# 시스템 빌드 도구 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# 컨테이너 포트 설정
EXPOSE 7777

# gunicorn으로 앱 실행
CMD ["gunicorn", "--bind", "0.0.0.0:7777", "app:app"]
