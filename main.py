# main.py
# 4단계: PM 에이전트를 포함한 심화된 상호작용 시나리오 실행

import time
from models import World, Agent
from llm_client import GeminiClient
from database import MemoryDB
from config import GEMINI_API_KEY

def run_simulation():
    """시뮬레이션을 초기화하고 실행합니다."""
    llm_client = GeminiClient(api_key=GEMINI_API_KEY)
    office_world = World(description="AI 스타트업의 작은 사무실")

    # 에이전트 역할 정의
    john_desc = "버그 수정에 책임이 있는 시니어 개발자. 할당된 작업에 집중한다."
    jane_desc = "사용자 피드백을 검토하고 버그를 찾아내는 QA 기획자. 문제 발생 시 PM에게 보고한다."
    chris_desc = "프로젝트 전체를 관리하는 프로젝트 매니저(PM). 팀원에게 작업을 할당하고 진행 상황을 확인한다."

    # 에이전트 및 메모리 DB 생성
    agents_data = {
        "John": {"desc": john_desc, "location": "개발팀 자리"},
        "Jane": {"desc": jane_desc, "location": "개발팀 자리"},
        "Chris": {"desc": chris_desc, "location": "회의실"}
    }
    
    for name, data in agents_data.items():
        memory = MemoryDB(agent_name=name)
        memory.clear_memory()
        agent = Agent(name=name, description=data["desc"], llm_client=llm_client, memory_db=memory)
        office_world.add_agent(agent, data["location"])

    print("\n--- 시뮬레이션 시작 ---")
    
    bug_discovered = False
    
    for i in range(15): # 상호작용을 충분히 관찰하기 위해 틱 증가
        print(f"\n{'='*10} Tick {i+1} {'='*10}")
        
        # Tick 2에 Jane이 버그 발견
        if i == 1 and not bug_discovered:
            print("\n>>> [이벤트 발생] Jane이 테스트 중 치명적인 버그를 발견했습니다! <<<\n")
            office_world.agents["Jane"].add_memory("중요한 발견: '로그인 기능'이 사용자 테스트에서 실패하는 것을 확인했다. PM에게 보고해야 한다.")
            bug_discovered = True

        agent_names = list(office_world.agents.keys())
        for agent_name in agent_names:
            if agent_name not in office_world.agents: continue
            agent = office_world.agents[agent_name]
            
            print(f"\n--- {agent.name}의 턴 ---")
            action = agent.plan_and_act(office_world)
            office_world.execute_action(agent, action)
            
            time.sleep(5) # 프롬프트가 매우 복잡해졌으므로 LLM 응답 시간 고려
            
    print(f"\n{'='*10} 시뮬레이션 종료 {'='*10}\n")
    print(f"최종 프로젝트 상태: {office_world.project_status}")
    print(f"John의 최종 작업 목록: {office_world.agents['John'].task_list}")

if __name__ == "__main__":
    run_simulation()
