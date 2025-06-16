# ui/Dockerfile
FROM python:3.10-slim

WORKDIR /app                              # 컨테이너 내부 작업 디렉터리

# 시스템 빌드툴 설치 (선택)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY ui/requirements.txt .               # 의존성 목록 복사
RUN pip install --no-cache-dir -r requirements.txt  # 패키지 설치

COPY ui/ .                                # 앱 소스 복사

EXPOSE 7777                               # 외부에 개방할 포트

CMD ["gunicorn", "--bind", "0.0.0.0:7777", "app:app"]
