# database.py
# 데이터베이스 연결 및 설정을 관리합니다.
# 필요한 라이브러리 설치: pip install psycopg2-binary chromadb

import psycopg2
import chromadb
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def get_postgres_connection():
    """PostgreSQL 데이터베이스에 연결하고 커넥션 객체를 반환합니다."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("PostgreSQL에 성공적으로 연결되었습니다.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"PostgreSQL 연결 오류: {e}")
        print("데이터베이스가 실행 중이고 config.py의 정보가 정확한지 확인하세요.")
        return None

def get_chroma_client():
    """ChromaDB 클라이언트를 초기화하고 반환합니다."""
    # 로컬 디스크에 데이터를 저장하는 영구 클라이언트를 생성합니다.
    client = chromadb.PersistentClient(path="./chroma_db")
    print("ChromaDB 클라이언트가 성공적으로 초기화되었습니다.")
    return client

if __name__ == '__main__':
    # 이 파일이 직접 실행될 때 연결 테스트를 수행합니다.
    pg_conn = get_postgres_connection()
    if pg_conn:
        pg_conn.close()
        print("PostgreSQL 연결 테스트 완료.")

    chroma_client = get_chroma_client()
    print(f"ChromaDB 컬렉션 목록: {chroma_client.list_collections()}")
    print("ChromaDB 연결 테스트 완료.")
