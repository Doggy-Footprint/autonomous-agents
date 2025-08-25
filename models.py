# models.py
# 시뮬레이션의 핵심 데이터 구조인 Agent와 World 클래스를 정의합니다.

import datetime

class World:
    """시뮬레이션 세계를 정의하고 관리합니다."""
    def __init__(self, description="작은 가상 오피스 공간"):
        self.description = description
        self.agents = {}  # {agent_name: Agent_instance}
        # 간단한 공간 표현: {location_name: [agent_name_1, agent_name_2]}
        self.locations = {
            "개발팀 자리": [],
            "휴게실": [],
            "회의실": []
        }
        print(f"'{self.description}' 세계가 생성되었습니다.")

    def add_agent(self, agent, location):
        """세계에 에이전트를 추가합니다."""
        if agent.name in self.agents:
            print(f"오류: '{agent.name}' 에이전트는 이미 존재합니다.")
            return
        if location not in self.locations:
            print(f"오류: '{location}'은(는) 존재하지 않는 장소입니다.")
            return

        self.agents[agent.name] = agent
        self.locations[location].append(agent.name)
        agent.location = location
        print(f"'{agent.name}' 에이전트가 '{location}'에 추가되었습니다.")

    def get_location_state(self, location):
        """특정 장소의 상태를 텍스트로 반환합니다."""
        if location not in self.locations:
            return f"'{location}'은(는) 알 수 없는 장소입니다."

        agent_names = self.locations[location]
        if not agent_names:
            return f"'{location}'에는 아무도 없습니다."
        else:
            return f"'{location}'에는 {', '.join(agent_names)}이(가) 있습니다."


class Agent:
    """자율적으로 행동하는 에이전트를 정의합니다."""
    def __init__(self, name, description):
        self.name = name
        self.description = description # 에이전트의 역할이나 성격 (e.g., "꼼꼼한 성격의 시니어 개발자")
        self.location = None # 현재 위치
        # Phase 1에서는 메모리를 간단한 리스트로 구현합니다.
        self.memory_stream = []
        print(f"'{self.name}' 에이전트가 생성되었습니다. ({self.description})")

    def add_memory(self, observation):
        """에이전트의 기억 스트림에 관찰 결과를 추가합니다."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        memory_entry = f"[{timestamp}] {observation}"
        self.memory_stream.append(memory_entry)
        print(f"[{self.name}의 기억 추가] {observation}")

    def perceive(self, world):
        """자신이 속한 세계의 주변 환경을 인식합니다."""
        if not self.location:
            return

        # 자신의 위치에 대한 상태를 관찰
        location_state = world.get_location_state(self.location)
        self.add_memory(location_state)
