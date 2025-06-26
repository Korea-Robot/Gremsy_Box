# Dockerfile
FROM gremsy_api:0.2.0

# 작업 디렉토리 설정
WORKDIR /app

# app.py를 app2 디렉토리에 복사
COPY app.py /app/app2/app.py

# # 포트 노출 (기본값, 환경변수로 오버라이드 가능)
# EXPOSE 8000

# 환경변수 기본값 설정
ENV PORT=8000

# Python 애플리케이션 실행
CMD ["sh", "-c", "cd /app/app2 && python app.py"]