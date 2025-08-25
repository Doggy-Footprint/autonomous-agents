# models.py
# 시뮬레이션의 핵심 데이터 구조인 Agent와 World 클래스를 정의합니다.

import datetime
import re

# World 클래스는 이전 버전과 동일하므로 생략합니다.
# (실제 코드에서는 World 클래스 코드가 이 부분에 있어야 합니다)
class World:
    """시뮬레이션 세계를 정의하고 관리합니다."""
    def __init__(self, description="작은 가상 오피스 공간"):
        self.description = description
        self.agents = {}
        self.locations = {"개발팀 자리": [], "휴게실": [], "회의실": []}
        print(f"'{self.description}' 세계가 생성되었습니다.")
    def add_agent(self, agent, location):
        if agent.name in self.agents: return
        if location not in self.locations: return
        self.agents[agent.name] = agent
        self.locations[location].append(agent.name)
        agent.location = location
        print(f"'{agent.name}' 에이전트가 '{location}'에 추가되었습니다.")
    def get_location_state(self, location):
        if location not in self.locations: return f"'{location}'은(는) 알 수 없는 장소입니다."
        agent_names = [name for name in self.locations[location]]
        return f"'{location}'에는 {', '.join(agent_names)}이(가) 있습니다." if agent_names else f"'{location}'에는 아무도 없습니다."
    def execute_action(self, agent, action_string):
        print(f"[{agent.name}의 행동 실행] {action_string}")
        move_match = re.match(r"MOVE to (.*)", action_string, re.IGNORECASE)
        say_match = re.match(r"SAY: (.*)", action_string, re.IGNORECASE)
        do_match = re.match(r"DO: (.*)", action_string, re.IGNORECASE)
        observation = ""
        if move_match:
            new_location = move_match.group(1).strip()
            if new_location in self.locations:
                old_location = agent.location
                if agent.name in self.locations[old_location]: self.locations[old_location].remove(agent.name)
                self.locations[new_location].append(agent.name)
                agent.location = new_location
                observation = f"{agent.name}이(가) {old_location}에서 {new_location}(으)로 이동했습니다."
            else: observation = f"{agent.name}이(가) {new_location}(으)로 이동하려 했지만 실패했습니다."
        elif say_match: observation = f"{agent.name}이(가) 말합니다: \"{say_match.group(1).strip()}\""
        elif do_match: observation = f"{agent.name}이(가) {do_match.group(1).strip()}."
        else: observation = f"{agent.name}이(가) 알 수 없는 행동('{action_string}')을 시도합니다."
        self.broadcast_observation(agent, observation)
    def broadcast_observation(self, acting_agent, observation):
        for agent in self.agents.values():
            if agent.location == acting_agent.location:
                agent.add_memory(observation)

class Agent:
    """자율적으로 행동하는 에이전트를 정의합니다. 장기 기억과 성찰 기능이 추가되었습니다."""
    def __init__(self, name, description, llm_client, memory_db):
        self.name = name
        self.description = description
        self.llm_client = llm_client
        self.memory_db = memory_db
        self.location = None
        
        # 성찰을 위한 변수
        self.reflection_threshold = 50 # 중요도 합계가 이 값을 넘으면 성찰 시작
        self.recent_importance_sum = 0
        self.recent_memories_for_reflection = []

        print(f"'{self.name}' 에이전트(기억/성찰 기능 탑재)가 생성되었습니다.")

    def add_memory(self, observation):
        """관찰 결과를 기억 DB에 중요도와 함께 추가합니다."""
        importance_score = self._calculate_importance(observation)
        timestamp = datetime.datetime.now()
        
        metadata = {
            "timestamp": timestamp.isoformat(),
            "type": "observation",
            "importance": importance_score
        }
        self.memory_db.add_memory(observation, metadata)
        print(f"[{self.name}의 기억 추가 (중요도: {importance_score})] {observation}")

        # 성찰 트리거 확인
        self.recent_importance_sum += importance_score
        self.recent_memories_for_reflection.append(observation)
        if self.recent_importance_sum >= self.reflection_threshold:
            self.reflect()

    def _calculate_importance(self, memory_text):
        """LLM을 사용해 기억의 중요도를 1-10 사이의 점수로 평가합니다."""
        prompt = f"""
당신은 AI 에이전트의 사고 과정을 보조하는 분석 시스템입니다.
다음 문장이 에이전트의 장기적인 목표나 행동에 얼마나 중요한지 1(일상적)에서 10(매우 중요) 사이의 정수로 평가해주세요.
오직 숫자만 응답하세요.

문장: "{memory_text}"
중요도:
"""
        response = self.llm_client.generate_response(prompt)
        try:
            return int(response)
        except (ValueError, TypeError):
            return 3 # 변환 실패 시 기본값

    def reflect(self):
        """최근의 중요한 기억들을 바탕으로 고차원적인 통찰(성찰)을 생성합니다."""
        print(f"\n--- [{self.name}의 성찰 시작] (누적 중요도: {self.recent_importance_sum}) ---")
        
        memories_str = "\n".join(self.recent_memories_for_reflection)
        prompt = f"""
당신은 '{self.name}' AI 에이전트입니다.
다음은 당신의 최근 경험들입니다:
{memories_str}

이 경험들을 바탕으로 얻을 수 있는 3가지 중요한 결론이나 통찰을 요약해주세요.
이 통찰은 당신의 미래 행동에 지침이 될 것입니다.
"""
        reflection_text = self.llm_client.generate_response(prompt)
        
        # 생성된 성찰을 다시 기억 DB에 추가
        reflection_importance = 10 # 성찰은 항상 중요도가 높음
        metadata = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "reflection",
            "importance": reflection_importance
        }
        self.memory_db.add_memory(f"성찰: {reflection_text}", metadata)
        print(f"[{self.name}의 성찰 완료] {reflection_text}")

        # 성찰 관련 변수 초기화
        self.recent_importance_sum = 0
        self.recent_memories_for_reflection = []
        print("--- 성찰 종료 ---\n")

    def perceive(self, world):
        """자신이 속한 세계의 주변 환경을 인식합니다."""
        if not self.location: return
        location_state = world.get_location_state(self.location)
        self.add_memory(location_state)

    def plan_and_act(self, world):
        """기억 DB에서 관련 정보를 검색하여 행동을 계획하고 실행합니다."""
        if not self.llm_client: return "DO: 가만히 있는다."

        # 현재 상황과 가장 관련 있는 기억들을 검색
        current_situation = f"현재 위치: {self.location}. {world.get_location_state(self.location)}"
        retrieved_memories = self.memory_db.retrieve_memories(current_situation, n_results=5)
        memories_str = "\n".join(retrieved_memories)

        available_locations = ", ".join(world.locations.keys())

        prompt = f"""
당신은 '{self.name}'이며, '{self.description}' 역할을 수행하는 AI 에이전트입니다.
현재 상황: {current_situation}

다음은 현재 상황과 관련하여 당신의 기억 속에서 인출된 정보입니다:
{memories_str}

이 모든 정보를 종합하여, 다음에 할 가장 적절하고 구체적인 단일 행동을 결정해주세요.
행동 형식:
- MOVE to [장소] (이동 가능한 장소: {available_locations})
- SAY: [메시지]
- DO: [행동 서술]

오직 행동 문자열 하나만 응답하세요.
"""
        action = self.llm_client.generate_response(prompt)
        return action
