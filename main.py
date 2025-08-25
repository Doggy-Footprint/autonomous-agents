# main.py
# 스타듀밸리 펠리칸 타운을 배경으로 한 자율 에이전트 시뮬레이션

import time
from models import World, Agent
from llm_client import GeminiClient
from database import MemoryDB
from config import GEMINI_API_KEY

def run_stardew_simulation():
    """시뮬레이션을 초기화하고 실행합니다."""
    llm_client = GeminiClient(api_key=GEMINI_API_KEY)
    
    # 월드 배경을 펠리칸 타운으로 변경
    pelican_town = World(description="스타듀밸리의 펠리칸 타운")
    # 장소 변경
    pelican_town.locations = {
        "농장": [],
        "잡화점": [],
        "촌장의 집": []
    }

    # 에이전트 역할 정의 (스타듀밸리 캐릭터 기반)
    player_desc = "최근 펠리칸 타운으로 귀농하여 농장을 가꾸기 시작한 플레이어. 마을 사람들과 친해지고 싶어한다."
    maru_desc = "호기심 많고 발명에 재능이 있는 과학자. 아버지의 가게에서 일하며 틈틈이 새로운 것을 만든다."
    lewis_desc = "펠리칸 타운의 촌장. 마을의 대소사를 챙기며 주민들의 안위를 걱정한다."

    # 에이전트 및 메모리 DB 생성
    agents_data = {
        "Player": {"desc": player_desc, "location": "농장"},
        "Maru": {"desc": maru_desc, "location": "잡화점"},
        "Lewis": {"desc": lewis_desc, "location": "촌장의 집"}
    }
    
    for name, data in agents_data.items():
        memory = MemoryDB(agent_name=name)
        memory.clear_memory()
        agent = Agent(name=name, description=data["desc"], llm_client=llm_client, memory_db=memory)
        pelican_town.add_agent(agent, data["location"])

    print("\n--- 스타듀밸리 시뮬레이션 시작 ---")
    
    event_triggered = False
    
    for i in range(15): # 상호작용을 충분히 관찰하기 위해 틱 증가
        print(f"\n{'='*10} Tick {i+1} {'='*10}")
        
        # Tick 3에 '마을 축제' 계획 이벤트 발생
        if i == 2 and not event_triggered:
            print("\n>>> [이벤트 발생] 촌장 루이스가 곧 다가올 마을 축제에 대한 아이디어를 떠올렸습니다! <<<\n")
            pelican_town.agents["Lewis"].add_memory("중요한 생각: 곧 있을 마을 축제를 성공적으로 개최하기 위해 주민들의 도움이 필요하다. 특히 새로운 주민인 Player에게 말을 걸어봐야겠다.")
            event_triggered = True

        agent_names = list(pelican_town.agents.keys())
        for agent_name in agent_names:
            if agent_name not in pelican_town.agents: continue
            agent = pelican_town.agents[agent_name]
            
            print(f"\n--- {agent.name}의 턴 ---")
            action = agent.plan_and_act(pelican_town)
            pelican_town.execute_action(agent, action)
            
            time.sleep(5) # 프롬프트가 매우 복잡해졌으므로 LLM 응답 시간 고려
            
    print(f"\n{'='*10} 시뮬레이션 종료 {'='*10}\n")
    print(f"최종 프로젝트 상태: {pelican_town.project_status if hasattr(pelican_town, 'project_status') else '없음'}")

if __name__ == "__main__":
    run_stardew_simulation()
