# models.py
# 시뮬레이션의 핵심 데이터 구조인 Agent와 World 클래스를 정의합니다.

import datetime
import re

class World:
    """시뮬레이션 세계를 정의하고 관리합니다."""
    def __init__(self, description="작은 가상 오피스 공간"):
        self.description = description
        self.agents = {}  # {agent_name: Agent_instance}
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

        agent_names = [name for name in self.locations[location]]
        if not agent_names:
            return f"'{location}'에는 아무도 없습니다."
        else:
            return f"'{location}'에는 {', '.join(agent_names)}이(가) 있습니다."

    def execute_action(self, agent, action_string):
        """에이전트의 행동을 해석하고 세계 상태를 업데이트합니다."""
        print(f"[{agent.name}의 행동 실행] {action_string}")
        
        # 행동 문자열 파싱 (정규표현식 사용)
        move_match = re.match(r"MOVE to (.*)", action_string, re.IGNORECASE)
        say_match = re.match(r"SAY: (.*)", action_string, re.IGNORECASE)
        do_match = re.match(r"DO: (.*)", action_string, re.IGNORECASE)

        observation = ""

        if move_match:
            new_location = move_match.group(1).strip()
            if new_location in self.locations:
                old_location = agent.location
                # 이전 위치에서 에이전트 제거
                if agent.name in self.locations[old_location]:
                    self.locations[old_location].remove(agent.name)
                # 새 위치에 에이전트 추가
                self.locations[new_location].append(agent.name)
                agent.location = new_location
                observation = f"{agent.name}이(가) {old_location}에서 {new_location}(으)로 이동했습니다."
            else:
                observation = f"{agent.name}이(가) {new_location}(으)로 이동하려 했지만 실패했습니다."

        elif say_match:
            message = say_match.group(1).strip()
            observation = f"{agent.name}이(가) 말합니다: \"{message}\""

        elif do_match:
            action_desc = do_match.group(1).strip()
            observation = f"{agent.name}이(가) {action_desc}."

        else:
            observation = f"{agent.name}이(가) 알 수 없는 행동('{action_string}')을 시도합니다."

        # 행동의 결과를 주변 에이전트들이 인식하게 함
        self.broadcast_observation(agent, observation)

    def broadcast_observation(self, acting_agent, observation):
        """행동의 결과를 해당 장소의 모든 에이전트에게 전달합니다."""
        for agent in self.agents.values():
            # 같은 장소에 있는 다른 에이전트와 자기 자신에게 관찰 결과 추가
            if agent.location == acting_agent.location:
                agent.add_memory(observation)


class Agent:
    """자율적으로 행동하는 에이전트를 정의합니다."""
    def __init__(self, name, description, llm_client):
        self.name = name
        self.description = description
        self.llm_client = llm_client
        self.location = None
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
        location_state = world.get_location_state(self.location)
        self.add_memory(location_state)

    def plan_and_act(self, world):
        """LLM을 사용하여 현재 상황에 맞는 행동을 계획하고 실행합니다."""
        if not self.llm_client:
            return "DO: 가만히 있는다."

        # LLM에게 전달할 프롬프트 생성
        recent_memories = "\n".join(self.memory_stream[-5:]) # 최근 5개의 기억만 사용
        available_locations = ", ".join(world.locations.keys())

        prompt = f"""
당신은 '{self.name}'이며, '{self.description}' 역할을 수행하는 AI 에이전트입니다.
현재 당신의 위치는 '{self.location}'입니다.

다음은 당신의 최근 기억들입니다:
{recent_memories}

이 상황을 바탕으로, 당신이 다음에 할 가장 적절하고 구체적인 단일 행동을 결정해주세요.
선택할 수 있는 행동 형식은 다음과 같습니다:
- MOVE to [장소] (이동 가능한 장소: {available_locations})
- SAY: [메시지]
- DO: [행동 서술] (예: 코딩을 시작한다, 커피를 내린다)

오직 행동 문자열 하나만 응답하세요. 예를 들어 'MOVE to 휴게실' 또는 'DO: 동료의 코드를 리뷰한다' 와 같이 응답해야 합니다.
"""
        
        # LLM 호출하여 행동 결정
        action = self.llm_client.generate_response(prompt)
        return action
