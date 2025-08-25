# main.py
# 시뮬레이션의 메인 루프를 실행하는 파일입니다.

import time
from models import World, Agent
from llm_client import GeminiClient
from database import MemoryDB
from config import GEMINI_API_KEY

def run_simulation():
    """시뮬레이션을 초기화하고 실행합니다."""
    # 0. LLM 클라이언트 초기화
    try:
        llm_client = GeminiClient(api_key=GEMINI_API_KEY)
    except ValueError as e:
        print(f"시뮬레이션 시작 실패: {e}")
        return

    # 1. 세계 생성
    office_world = World(description="AI 스타트업의 작은 사무실")

    # 2. 에이전트별 메모리 DB 생성 및 초기화
    john_memory = MemoryDB(agent_name="John")
    jane_memory = MemoryDB(agent_name="Jane")
    john_memory.clear_memory() # 시뮬레이션 시작 전 이전 기억 삭제
    jane_memory.clear_memory()

    # 3. 에이전트 생성 (MemoryDB 주입)
    john = Agent(name="John", description="새로운 기능 개발에 몰두하는 열정적인 개발자", llm_client=llm_client, memory_db=john_memory)
    jane = Agent(name="Jane", description="사용자 경험을 중요시하는 꼼꼼한 기획자", llm_client=llm_client, memory_db=jane_memory)

    # 4. 초기 상태 설정
    office_world.add_agent(john, "개발팀 자리")
    office_world.add_agent(jane, "개발팀 자리")

    # 5. 시뮬레이션 루프 (더 길게 실행하여 성찰 과정 관찰)
    print("\n--- 시뮬레이션 시작 ---")
    for i in range(10): # 틱 횟수를 늘려 성찰이 일어날 기회를 줌
        print(f"\n{'='*10} Tick {i+1} {'='*10}")
        
        agent_names = list(office_world.agents.keys())
        for agent_name in agent_names:
            if agent_name not in office_world.agents: continue
            agent = office_world.agents[agent_name]
            
            print(f"\n--- {agent.name}의 턴 ---")
            agent.perceive(office_world)
            action = agent.plan_and_act(office_world)
            office_world.execute_action(agent, action)
            
            time.sleep(3) # LLM 호출이 많아졌으므로 대기 시간 증가
            
    print(f"\n{'='*10} 시뮬레이션 종료 {'='*10}\n")

    # 최종 상태 확인 (ChromaDB에 저장된 내용을 직접 확인하는 것이 더 정확함)
    print("John의 관련 기억 (현재 위치 기준):")
    retrieved = john_memory.retrieve_memories(f"John은 현재 {john.location}에 있다.", n_results=5)
    for mem in retrieved:
        print(f"- {mem}")

if __name__ == "__main__":
    run_simulation()
