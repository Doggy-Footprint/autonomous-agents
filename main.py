# main.py
# 시뮬레이션의 메인 루프를 실행하는 파일입니다.

import time
from models import World, Agent
from llm_client import GeminiClient
from config import GEMINI_API_KEY

def run_simulation():
    """시뮬레이션을 초기화하고 실행합니다."""
    # 0. LLM 클라이언트 초기화
    try:
        llm_client = GeminiClient(api_key=GEMINI_API_KEY)
    except ValueError as e:
        print(f"시뮬레이션 시작 실패: {e}")
        return

    # 1. 세계와 에이전트 생성
    office_world = World(description="AI 스타트업의 작은 사무실")
    john = Agent(name="John", description="새로운 기능 개발에 몰두하는 열정적인 개발자", llm_client=llm_client)
    jane = Agent(name="Jane", description="사용자 경험을 중요시하는 꼼꼼한 기획자", llm_client=llm_client)

    # 2. 초기 상태 설정
    office_world.add_agent(john, "개발팀 자리")
    office_world.add_agent(jane, "개발팀 자리")

    # 3. 시뮬레이션 루프
    print("\n--- 시뮬레이션 시작 ---")
    # 5번의 틱(tick) 동안 시뮬레이션을 실행합니다.
    for i in range(5):
        print(f"\n{'='*10} Tick {i+1} {'='*10}")
        
        # 모든 에이전트에 대해 인식-행동 사이클 실행
        # 매 틱마다 에이전트 순서를 섞어주면 더 역동적인 상호작용을 만들 수 있습니다.
        # import random
        # agent_names = list(office_world.agents.keys())
        # random.shuffle(agent_names)
        
        agent_names = list(office_world.agents.keys())
        for agent_name in agent_names:
            # 루프 도중 에이전트가 제거될 경우를 대비
            if agent_name not in office_world.agents:
                continue
            
            agent = office_world.agents[agent_name]
            
            print(f"\n--- {agent.name}의 턴 ---")
            # (1) 인식 (Perceive)
            agent.perceive(office_world)

            # (2) 계획 및 행동 (Plan & Act)
            action = agent.plan_and_act(office_world)
            
            # (3) 행동 실행 (Execute)
            office_world.execute_action(agent, action)
            
            # API 호출 속도 조절 및 로그 확인을 위한 대기
            # 실제 시뮬레이션에서는 이 시간을 조절하거나 제거할 수 있습니다.
            time.sleep(2) 
            
    print(f"\n{'='*10} 시뮬레이션 종료 {'='*10}\n")

    # 최종 상태 확인
    for agent in office_world.agents.values():
        print(f"--- {agent.name}의 최종 기억 ---")
        for memory in agent.memory_stream:
            print(memory)
        print("-" * (len(agent.name) + 15))


if __name__ == "__main__":
    run_simulation()
