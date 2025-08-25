# main.py
# 시뮬레이션의 메인 루프를 실행하는 파일입니다.

import time
from models import World, Agent

def run_simulation():
    """시뮬레이션을 초기화하고 실행합니다."""
    # 1. 세계와 에이전트 생성
    office_world = World(description="AI 스타트업의 작은 사무실")
    hwansu = Agent(name="Hwansu", description="새로운 기능 개발에 몰두하는 열정적인 개발자")

    # 2. 초기 상태 설정
    office_world.add_agent(hwansu, "개발팀 자리")

    # 3. 시뮬레이션 루프 (Phase 1에서는 간단히 몇 번만 실행)
    print("\n--- 시뮬레이션 시작 ---")
    for i in range(10):
        print(f"\n[Tick {i+1}]")
        
        # 모든 에이전트에 대해 인식-행동 사이클 실행
        for agent_name, agent in office_world.agents.items():
            # (1) 인식 (Perceive)
            agent.perceive(office_world)

            # (2) 계획 및 행동 (Plan & Act) - Phase 2에서 구현 예정
            # action = agent.plan_and_act()
            # world.update(agent, action)
            
        time.sleep(1) # 각 틱 사이에 잠시 대기

    print("\n--- 시뮬레이션 종료 ---\n")

    # 최종 상태 확인
    print("최종 에이전트 기억:")
    for memory in hwansu.memory_stream:
        print(memory)


if __name__ == "__main__":
    run_simulation()
