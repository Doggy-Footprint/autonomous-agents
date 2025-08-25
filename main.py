# main.py
# 버그 발생 및 해결 시나리오를 실행하는 메인 루프입니다.

import time
from models import World, Agent
from llm_client import GeminiClient
from database import MemoryDB
from config import GEMINI_API_KEY

def run_simulation():
    """시뮬레이션을 초기화하고 실행합니다."""
    llm_client = GeminiClient(api_key=GEMINI_API_KEY)
    office_world = World(description="AI 스타트업의 작은 사무실")

    # 에이전트 역할 재정의
    john_desc = "버그 수정에 책임이 있는 시니어 개발자"
    jane_desc = "사용자 피드백을 검토하고 버그를 찾아내는 QA 기획자"

    john_memory = MemoryDB(agent_name="John")
    jane_memory = MemoryDB(agent_name="Jane")
    john_memory.clear_memory()
    jane_memory.clear_memory()

    john = Agent(name="John", description=john_desc, llm_client=llm_client, memory_db=john_memory)
    jane = Agent(name="Jane", description=jane_desc, llm_client=llm_client, memory_db=jane_memory)

    office_world.add_agent(john, "개발팀 자리")
    office_world.add_agent(jane, "개발팀 자리")

    print("\n--- 시뮬레이션 시작 ---")
    
    bug_reported = False
    
    for i in range(10):
        print(f"\n{'='*10} Tick {i+1} {'='*10}")
        
        # Tick 3에 버그 발견 이벤트 강제 주입
        if i == 2 and not bug_reported:
            print("\n>>> [이벤트 발생] Jane이 사용자 피드백에서 치명적인 버그를 발견했습니다! <<<\n")
            jane.add_memory("중요한 발견: 테스트 중 '로그인 기능'이 작동하지 않는 것을 확인했다.")
            bug_reported = True # 이벤트가 한 번만 발생하도록 플래그 설정

        agent_names = list(office_world.agents.keys())
        for agent_name in agent_names:
            if agent_name not in office_world.agents: continue
            agent = office_world.agents[agent_name]
            
            print(f"\n--- {agent.name}의 턴 ---")
            # perceive는 월드 상태를 보는 것이므로, broadcast_observation으로 대체 가능
            # agent.perceive(office_world) 
            action = agent.plan_and_act(office_world)
            office_world.execute_action(agent, action)
            
            time.sleep(4) # LLM 호출이 많고 프롬프트가 길어졌으므로 대기 시간 증가
            
    print(f"\n{'='*10} 시뮬레이션 종료 {'='*10}\n")
    print(f"최종 프로젝트 상태: {office_world.project_status}")

if __name__ == "__main__":
    run_simulation()
