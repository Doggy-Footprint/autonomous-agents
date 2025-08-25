# config.py
# 이 파일에는 API 키, 데이터베이스 자격 증명 등 민감한 정보를 저장합니다.
# 실제 값으로 채워주세요.

import os
from dotenv import load_dotenv

load_dotenv()

# Google AI Studio (Gemini) API 키
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# PostgreSQL 데이터베이스 연결 정보
DB_NAME = "autonomous_agent_simulation"
DB_USER = "hwansu_agent"
DB_PASSWORD = '1234'
DB_HOST = "localhost"
DB_PORT = "5432"
