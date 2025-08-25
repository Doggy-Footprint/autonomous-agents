# database.py
# 데이터베이스 연결 및 설정을 관리합니다.
# 필요한 라이브러리 설치: pip install psycopg2-binary chromadb google-generativeai

import psycopg2
import chromadb
from chromadb.utils import embedding_functions
import uuid

from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, GEMINI_API_KEY

def get_postgres_connection():
    """PostgreSQL 데이터베이스에 연결하고 커넥션 객체를 반환합니다."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        print("PostgreSQL에 성공적으로 연결되었습니다.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"PostgreSQL 연결 오류: {e}")
        return None

class MemoryDB:
    """ChromaDB를 사용하여 에이전트의 기억을 관리하는 클래스."""
    def __init__(self, agent_name):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Google Gemini 임베딩 함수 설정
        self.embedding_fn = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=GEMINI_API_KEY)
        
        # 각 에이전트별로 고유한 컬렉션 생성
        collection_name = f"agent_{agent_name}_memory"
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )
        print(f"'{collection_name}' ChromaDB 컬렉션이 준비되었습니다.")

    def add_memory(self, memory_text, metadata):
        """기억을 ChromaDB에 추가합니다."""
        memory_id = str(uuid.uuid4())
        self.collection.add(
            documents=[memory_text],
            metadatas=[metadata],
            ids=[memory_id]
        )

    def retrieve_memories(self, query_text, n_results=5):
        """주어진 쿼리와 가장 관련성 높은 기억을 검색합니다."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        # 결과가 비어있을 경우를 대비한 안전장치 추가
        if not results or not results.get('ids') or not results['ids'][0]:
            return []
        return results['documents'][0]

    def clear_memory(self):
        """
        [수정된 부분] 에이전트의 모든 기억을 삭제합니다.
        컬렉션을 삭제/재생성하는 대신, 컬렉션 내의 모든 아이템을 삭제하여 오류를 우회합니다.
        """
        try:
            count = self.collection.count()
            if count == 0:
                print(f"'{self.collection.name}' 컬렉션은 이미 비어 있습니다.")
                return
            
            # 컬렉션의 모든 아이템 ID를 가져와서 삭제합니다.
            all_item_ids = self.collection.get()['ids']
            if all_item_ids:
                self.collection.delete(ids=all_item_ids)
                print(f"'{self.collection.name}' 컬렉션에서 {len(all_item_ids)}개의 기억을 삭제했습니다.")
        except Exception as e:
            print(f"기억 삭제 중 예상치 못한 오류 발생: {e}")

